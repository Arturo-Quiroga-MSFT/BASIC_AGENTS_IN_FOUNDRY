# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates a Weather Agent using real OpenWeatherMap API.
    The agent uses function calling to provide actual weather information.

USAGE:
    python weather_agent_sync.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv httpx

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model
    3) OPENWEATHER_API_KEY - Your OpenWeatherMap API key (get free at https://openweathermap.org/api)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool

# Add weather_tool directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "weather_tool"))
from shared_utils import get_real_weather

load_dotenv(Path(__file__).parent / ".env")

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    with project_client.get_openai_client() as openai_client:
        
        # Create function tool for weather
        weather_tool = FunctionTool(
            name="get_real_weather",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name or location (e.g., 'Seattle', 'London', 'Tokyo')"
                    }
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            description="Get real-time weather information for a city using OpenWeatherMap API",
            strict=True,
        )
        
        # Create weather agent
        agent = project_client.agents.create_version(
            agent_name="WeatherAgent",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="""You are a helpful weather assistant that provides real-time weather information.
                
When users ask about weather, use the get_real_weather function to fetch current conditions.
Always provide complete information including temperature, conditions, humidity, and wind speed.
Be conversational and helpful in your responses.""",
                tools=[weather_tool],
            ),
            description="Weather agent with real OpenWeatherMap API integration",
        )
        print(f"✅ Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        # Get city name from user
        city = input("\n🌍 Which city would you like to get weather information for? ")
        
        # Create conversation
        conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": f"What's the weather like in {city}?"}],
        )
        print(f"📝 Created conversation (id: {conversation.id})")

        # Get response (with function calling)
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",
        )
        
        # Handle function calls
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
                        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                        input=[{
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": result
                        }],
                    )
        
        print(f"\n💬 Agent: {response.output_text}\n")
        
        # Ask for another city
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
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
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
                            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                            input=[{
                                "type": "function_call_output",
                                "call_id": item.call_id,
                                "output": result
                            }],
                        )
            
            print(f"\n💬 Agent: {response.output_text}\n")

        # Cleanup
        #openai_client.conversations.delete(conversation_id=conversation.id)
        #print("🗑️  Conversation deleted")

    #project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    #print("🗑️  Agent deleted")
