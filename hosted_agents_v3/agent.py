#!/usr/bin/env python3
"""
Simple Hosted Agent using Azure AI Agent Framework and Hosting Adapter

This agent demonstrates:
- Integration with Foundry hosting adapter
- Automatic HTTP service exposure
- OpenTelemetry instrumentation
- Conversation management

Based on Microsoft Foundry official samples:
https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents/agent-framework
"""

import os
from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient
from azure.ai.agentserver.agentframework import from_agent_framework
from azure.identity import DefaultAzureCredential

# Load environment variables from .env file for local development
load_dotenv()


def create_agent():
    """
    Create and return a ChatAgent.
    
    This agent uses Azure OpenAI and demonstrates:
    - Simple conversational capabilities
    - Integration with Foundry hosting adapter
    - Proper authentication with DefaultAzureCredential
    """
    
    # Validate required environment variables
    required_env_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",
    ]
    
    for env_var in required_env_vars:
        if env_var not in os.environ or not os.environ[env_var]:
            raise ValueError(
                f"{env_var} environment variable must be set.\n"
                f"Copy .env.example to .env and fill in your Azure details."
            )
    
    print(f"Creating agent...")
    print(f"  OpenAI Endpoint: {os.environ['AZURE_OPENAI_ENDPOINT']}")
    print(f"  Chat Deployment: {os.environ['AZURE_OPENAI_CHAT_DEPLOYMENT_NAME']}")
    
    # Create the Azure OpenAI Chat Client with proper credential
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential()
    )
    
    # Create the agent
    agent = chat_client.create_agent(
        name="SimpleHostedAgent",
        instructions="""You are a helpful AI assistant deployed as a hosted agent on Microsoft Foundry.

Your capabilities:
- Answer questions clearly and concisely
- Provide helpful information on various topics
- Maintain context across multiple turns in a conversation
- Be friendly and professional

When responding:
- Keep answers focused and relevant
- Ask clarifying questions if needed
- Admit when you don't know something
- Cite sources when providing factual information
"""
    )
    
    print(f"  Agent created: {agent.name}")
    
    return agent


def main():
    """
    Main entry point for the hosted agent.
    
    This function:
    1. Creates the agent
    2. Wraps it with the hosting adapter
    3. Starts the HTTP server on port 8088
    """
    
    print("="*60)
    print("STARTING HOSTED AGENT")
    print("="*60)
    print(f"Python unbuffered output enabled")
    print(f"Port: {os.environ.get('PORT', '8088')}")
    
    try:
        # Create the agent
        agent = create_agent()
        
        print(f"\n✅ Agent ready!")
        print(f"\nHosting adapter will start on: http://0.0.0.0:8088")
        print(f"Health endpoint: http://0.0.0.0:8088/readiness")
        print(f"Test with: POST http://0.0.0.0:8088/responses")
        print(f"\nPress Ctrl+C to stop the server...")
        print("="*60 + "\n")
        
        # Run the agent as a hosted agent
        # The from_agent_framework adapter:
        # - Starts an HTTP server on port 8088
        # - Exposes the agent via the Responses API
        # - Handles conversation management
        # - Provides OpenTelemetry instrumentation
        # - Provides /readiness and /health endpoints
        from_agent_framework(agent).run()
        
    except KeyboardInterrupt:
        print("\n\nShutting down agent...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
