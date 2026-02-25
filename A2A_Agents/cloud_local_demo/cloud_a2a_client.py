"""
Cloud A2A Client — connects to a remote A2A agent via MAF.

This script uses Microsoft Agent Framework's A2AAgent to discover and
communicate with an A2A-compliant agent (e.g., the local_a2a_server.py
running Foundry Local).

Architecture:
  ┌──────────────────────────────┐     A2A protocol      ┌──────────────────────┐
  │  THIS SCRIPT (client)        │ ◄─────────────────► │  A2A Server          │
  │                              │                      │  (local_a2a_server)  │
  │  agent-framework-a2a         │                      │  port 9999           │
  │  A2AAgent  ·  A2ACardResolver│                      │  Foundry Local       │
  └──────────────────────────────┘                      └──────────────────────┘

Prerequisites:
  pip install -r requirements.txt

Usage:
  python cloud_a2a_client.py [--host HOST_URL]

  Examples:
    python cloud_a2a_client.py                                  # localhost:9999
    python cloud_a2a_client.py --host https://abc.ngrok.io      # remote via tunnel
"""

import argparse
import asyncio
import logging

import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def discover_agent(host: str):
    """Resolve the remote agent's card to learn about its capabilities."""
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        resolver = A2ACardResolver(httpx_client=http_client, base_url=host)
        card = await resolver.get_agent_card()
        print(f"\n{'='*60}")
        print(f"  Agent Discovered via A2A")
        print(f"{'='*60}")
        print(f"  Name:        {card.name}")
        print(f"  Description: {card.description}")
        print(f"  Version:     {card.version}")
        print(f"  URL:         {card.url}")
        if card.skills:
            print(f"  Skills:")
            for skill in card.skills:
                print(f"    - {skill.name}: {skill.description}")
        print(f"{'='*60}\n")
        return card


async def interactive_chat(host: str, agent_card):
    """Run an interactive chat loop with the remote A2A agent."""
    async with A2AAgent(
        name=agent_card.name,
        description=agent_card.description,
        agent_card=agent_card,
        url=host,
    ) as agent:
        print("Type your messages below. Type 'quit' or 'exit' to stop.\n")

        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            print("Agent: ", end="", flush=True)
            try:
                response = await agent.run(user_input)
                for message in response.messages:
                    print(message.text)
            except Exception as e:
                print(f"\n[Error] {e}")

            print()  # blank line


async def single_query(host: str, agent_card, query: str):
    """Send a single query and print the response."""
    async with A2AAgent(
        name=agent_card.name,
        description=agent_card.description,
        agent_card=agent_card,
        url=host,
    ) as agent:
        print(f"Sending: {query}")
        print("---")
        response = await agent.run(query)
        for message in response.messages:
            print(f"Agent: {message.text}")


async def streaming_query(host: str, agent_card, query: str):
    """Send a query with streaming enabled to see incremental output."""
    async with A2AAgent(
        name=agent_card.name,
        description=agent_card.description,
        agent_card=agent_card,
        url=host,
    ) as agent:
        print(f"Sending (streaming): {query}")
        print("---")
        print("Agent: ", end="", flush=True)
        try:
            async with agent.run(query, stream=True) as stream:
                async for update in stream:
                    for content in update.contents:
                        if content.text:
                            print(content.text, end="", flush=True)
                final = await stream.get_final_response()
                print(f"\n\n[{len(final.messages)} message(s) received]")
        except Exception as e:
            # Streaming may not be supported by the server
            print(f"\n[Streaming not supported or error: {e}]")
            print("Falling back to non-streaming...")
            response = await agent.run(query)
            for message in response.messages:
                print(f"Agent: {message.text}")


async def main():
    parser = argparse.ArgumentParser(
        description="Connect to an A2A agent via Microsoft Agent Framework"
    )
    parser.add_argument(
        "--host",
        default="http://localhost:9999",
        help="URL of the A2A agent (default: http://localhost:9999)",
    )
    parser.add_argument(
        "--query",
        default=None,
        help="Send a single query instead of interactive mode",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Use streaming mode for the query",
    )
    args = parser.parse_args()

    # 1. Discover the agent
    agent_card = await discover_agent(args.host)

    # 2. Run in chosen mode
    if args.query:
        if args.stream:
            await streaming_query(args.host, agent_card, args.query)
        else:
            await single_query(args.host, agent_card, args.query)
    else:
        await interactive_chat(args.host, agent_card)


if __name__ == "__main__":
    asyncio.run(main())
