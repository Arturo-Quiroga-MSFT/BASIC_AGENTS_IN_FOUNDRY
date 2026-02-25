"""
Local A2A Server — Foundry Local as the LLM backend.

This script creates an A2A-compliant server powered by Foundry Local
(on-device ONNX inference). Any A2A client — including MAF's A2AAgent,
Copilot Studio, or the Foundry A2A Tool — can discover and talk to it.

Architecture:
  ┌──────────────────────────────────────┐
  │        A2A Server (port 9999)        │
  │  a2a-sdk  ·  Starlette  ·  uvicorn   │
  │                                      │
  │  AgentCard at /v1/card               │
  │  Messages at  /v1/message:stream     │
  │                                      │
  │  ┌──────────────────────────────┐    │
  │  │     Foundry Local backend    │    │
  │  │  foundry-local-sdk  ·  ONNX  │    │
  │  │  OpenAI-compatible endpoint  │    │
  │  └──────────────────────────────┘    │
  └──────────────────────────────────────┘

Prerequisites:
  1. Install Foundry Local CLI:
       winget install Microsoft.FoundryLocal   (Windows)
       brew install foundry-local               (macOS, when available)
     Or see: https://learn.microsoft.com/ai/foundry-local/get-started
  2. pip install -r requirements.txt

Usage:
  python local_a2a_server.py [--model MODEL_ALIAS] [--port PORT]

  Examples:
    python local_a2a_server.py                          # phi-4-mini, port 9999
    python local_a2a_server.py --model qwen2.5-0.5b     # lighter model
    python local_a2a_server.py --port 8888               # custom port
"""

import argparse
import asyncio
import logging

import uvicorn
from openai import AsyncOpenAI

from a2a.server.apps import A2AStarletteApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Foundry Local LLM wrapper
# ---------------------------------------------------------------------------

class FoundryLocalLLM:
    """Thin async wrapper around Foundry Local's OpenAI-compatible endpoint."""

    def __init__(self, model_alias: str = "phi-4-mini"):
        self.model_alias = model_alias
        self._client: AsyncOpenAI | None = None
        self._endpoint: str | None = None

    async def start(self):
        """Start the Foundry Local runtime and connect."""
        try:
            from foundry_local import FoundryLocalManager
            logger.info(f"Starting Foundry Local with model '{self.model_alias}'...")
            manager = FoundryLocalManager(self.model_alias)
            self._endpoint = manager.endpoint
            self._client = AsyncOpenAI(
                base_url=f"{self._endpoint}/v1",
                api_key="foundry-local",  # any non-empty string works
            )
            logger.info(f"Foundry Local ready at {self._endpoint}")
        except ImportError:
            # Fallback: assume Foundry Local is already running externally
            logger.warning(
                "foundry-local-sdk not installed. "
                "Assuming Foundry Local is running at http://localhost:5272"
            )
            self._endpoint = "http://localhost:5272"
            self._client = AsyncOpenAI(
                base_url=f"{self._endpoint}/v1",
                api_key="foundry-local",
            )

    async def chat(self, user_message: str, system_prompt: str | None = None) -> str:
        """Send a single-turn chat completion and return the text."""
        if not self._client:
            await self.start()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        response = await self._client.chat.completions.create(
            model=self.model_alias,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content or "(no response)"


# ---------------------------------------------------------------------------
# A2A AgentExecutor — bridges A2A protocol with Foundry Local
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a helpful local assistant running on the user's own device "
    "via Foundry Local. You are privacy-focused: all processing happens "
    "on-device and no data is sent to the cloud. You can answer general "
    "questions, summarize text, and help with code. Be concise and helpful."
)


class FoundryLocalAgentExecutor(AgentExecutor):
    """A2A AgentExecutor that delegates inference to Foundry Local."""

    def __init__(self, llm: FoundryLocalLLM):
        self.llm = llm

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Handle an incoming A2A message by running Foundry Local inference."""
        # Extract user text from the A2A message
        user_text = self._extract_text(context)
        logger.info(f"Received A2A message: {user_text[:100]}...")

        # Call Foundry Local
        response_text = await self.llm.chat(user_text, system_prompt=SYSTEM_PROMPT)
        logger.info(f"Foundry Local response: {response_text[:100]}...")

        # Send A2A response back
        await event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Cancel is not supported for this simple agent."""
        raise NotImplementedError("Cancel not supported")

    @staticmethod
    def _extract_text(context: RequestContext) -> str:
        """Pull the user's text from the A2A request context."""
        # The request context contains the message with parts
        message = context.message
        if message and message.parts:
            for part in message.parts:
                if hasattr(part, "text") and part.text:
                    return part.text
                # Handle the union type — part might be wrapped
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    return part.root.text
        return "(empty message)"


# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

def create_server(model_alias: str, port: int) -> A2AStarletteApplication:
    """Wire up the A2A server with Foundry Local backend."""

    llm = FoundryLocalLLM(model_alias=model_alias)

    # Pre-start Foundry Local (synchronously, before the server starts)
    asyncio.get_event_loop().run_until_complete(llm.start())

    # Define the agent's skill (what it can do)
    skill = AgentSkill(
        id="local_assistant",
        name="Local On-Device Assistant",
        description=(
            "A privacy-focused assistant running entirely on the user's device "
            "via Foundry Local. Handles general Q&A, summarization, and code help."
        ),
        tags=["local", "privacy", "foundry-local", "on-device"],
        examples=[
            "Summarize this text for me",
            "Help me write a Python function",
            "What is the A2A protocol?",
        ],
    )

    # Agent Card — how other agents discover this one
    agent_card = AgentCard(
        name="Foundry Local Agent",
        description=(
            f"An on-device AI agent powered by Foundry Local ({model_alias}). "
            "All inference runs locally — no data leaves the device."
        ),
        url=f"http://localhost:{port}/",
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    # Wire A2A protocol handler
    request_handler = DefaultRequestHandler(
        agent_executor=FoundryLocalAgentExecutor(llm),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    return server


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run a local A2A server backed by Foundry Local"
    )
    parser.add_argument(
        "--model",
        default="phi-4-mini",
        help="Foundry Local model alias (default: phi-4-mini)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9999,
        help="Port to serve the A2A endpoint (default: 9999)",
    )
    args = parser.parse_args()

    server = create_server(args.model, args.port)

    logger.info(f"Starting A2A server on port {args.port}...")
    logger.info(f"  Agent Card:  http://localhost:{args.port}/v1/card")
    logger.info(f"  Messages:    POST http://localhost:{args.port}/v1/message:stream")
    logger.info(f"  Model:       {args.model}")
    logger.info("")
    logger.info("Press Ctrl+C to stop.")

    uvicorn.run(server.build(), host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
