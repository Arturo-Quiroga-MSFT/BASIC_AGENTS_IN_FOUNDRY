# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Call a published WeatherAgent via the Responses API endpoint.
    This demonstrates how to interact with a published agent application.
    
    NOTE: Even published agents require the client to execute function calls
    and return results. The agent handles the logic, but execution happens client-side.

USAGE:
    python call_published_agent.py

    Before running:
    pip install "azure-ai-projects>=2.0.0b1" python-dotenv azure-identity

    Set environment variable:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Add weather_tool directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "weather_tool"))
from shared_utils import get_real_weather

load_dotenv(Path(__file__).parent / ".env")

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

# Published agent details
PUBLISHED_AGENT_NAME = "WeatherAgent"
PUBLISHED_AGENT_VERSION = "2"


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        
        print(f"🌐 Calling published agent: {PUBLISHED_AGENT_NAME} (v{PUBLISHED_AGENT_VERSION})")
        
        # Get user input
        city = input("\n🌍 Which city would you like to check the weather for? ")
        
        # Create conversation
        conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": f"What's the weather like in {city}?"}],
        )
        print(f"📝 Created conversation (id: {conversation.id})")

        # Call the published agent using agent reference
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent": {
                    "name": PUBLISHED_AGENT_NAME,
                    "version": PUBLISHED_AGENT_VERSION,
                    "type": "agent_reference"
                }
            },
            input="",
        )
        
        # Handle function calls (published agents still need client-side execution)
        if response.output:
            for item in response.output:
                if item.type == "function_call":
                    print(f"🔧 Function called: {item.name}")
                    
                    # Execute the function
                    import json
                    args = json.loads(item.arguments)
                    result = get_real_weather(**args)
                    print(f"🌤️  Weather data retrieved")
                    
                    # Submit function result back to agent
                    response = openai_client.responses.create(
                        conversation=conversation.id,
                        extra_body={
                            "agent": {
                                "name": PUBLISHED_AGENT_NAME,
                                "version": PUBLISHED_AGENT_VERSION,
                                "type": "agent_reference"
                            }
                        },
                        input=[{
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": result
                        }],
                    )
        
        print(f"\n💬 Agent response:\n{response.output_text}\n")
        
        # Follow-up question
        another_city = input("🌍 Want to check another city? Enter city name (or press Enter to skip): ")
        
        if another_city.strip():
            openai_client.conversations.items.create(
                conversation_id=conversation.id,
                items=[{"type": "message", "role": "user", "content": f"How about {another_city}?"}],
            )
            print("📝 Added follow-up question")

            # Get second response
            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={
                    "agent": {
                        "name": PUBLISHED_AGENT_NAME,
                        "version": PUBLISHED_AGENT_VERSION,
                        "type": "agent_reference"
                    }
                },
                input="",
            )
            
            # Handle function calls again
            if response.output:
                for item in response.output:
                    if item.type == "function_call":
                        print(f"🔧 Function called: {item.name}")
                        
                        import json
                        args = json.loads(item.arguments)
                        result = get_real_weather(**args)
                        print(f"🌤️  Weather data retrieved")
                        
                        response = openai_client.responses.create(
                            conversation=conversation.id,
                            extra_body={
                                "agent": {
                                    "name": PUBLISHED_AGENT_NAME,
                                    "version": PUBLISHED_AGENT_VERSION,
                                    "type": "agent_reference"
                                }
                            },
                            input=[{
                                "type": "function_call_output",
                                "call_id": item.call_id,
                                "output": result
                            }],
                        )
            
            print(f"\n💬 Agent response:\n{response.output_text}\n")
        
        print("✅ Done!")
        print(f"📋 Agent: {PUBLISHED_AGENT_NAME} v{PUBLISHED_AGENT_VERSION}")
        print("ℹ️  Note: Published agents define tools, but clients execute functions")
        
        # Cleanup (optional - comment out to keep conversation)
        #openai_client.conversations.delete(conversation_id=conversation.id)
        #print("🗑️  Conversation deleted")


if __name__ == "__main__":
    main()
