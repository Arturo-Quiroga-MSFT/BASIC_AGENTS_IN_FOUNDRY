#!/usr/bin/env python3
"""
Invoke Deployed Hosted Agent

This script invokes a deployed hosted agent using the Azure AI Projects SDK.
It demonstrates how to interact with a hosted agent after it's been deployed.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentReference
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME", "my-hosted-agent")
AGENT_VERSION = os.getenv("AGENT_VERSION", "1")


def validate_config() -> bool:
    """Validate required configuration."""
    
    if not PROJECT_ENDPOINT:
        print("❌ AZURE_AI_PROJECT_ENDPOINT is not set")
        return False
    
    return True


def invoke_agent(message: str):
    """
    Invoke the deployed hosted agent with a message.
    
    Args:
        message: The user message to send to the agent
    """
    
    print("="*60)
    print("INVOKE HOSTED AGENT")
    print("="*60)
    
    if not validate_config():
        return
    
    print(f"\nConfiguration:")
    print(f"  Project Endpoint: {PROJECT_ENDPOINT}")
    print(f"  Agent Name: {AGENT_NAME}")
    print(f"  Agent Version: {AGENT_VERSION}")
    print(f"\nUser Message: {message}")
    
    try:
        print("\n1. Authenticating...")
        credential = DefaultAzureCredential()
        
        print("2. Creating AI Project client...")
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential
        )
        
        print("3. Getting OpenAI client...")
        openai_client = client.get_openai_client()
        
        print("4. Sending message to agent...")
        # Use the OpenAI Responses API format with input parameter
        response = openai_client.responses.create(
            input=[{"role": "user", "content": message}],
            extra_body={
                "agent": AgentReference(
                    name=AGENT_NAME,
                    version=AGENT_VERSION
                ).as_dict()
            }
        )
        
        print("\n" + "="*60)
        print("AGENT RESPONSE")
        print("="*60)
        
        # Extract and display the response from the OpenAI Responses API format
        if hasattr(response, 'output') and response.output:
            for output_item in response.output:
                if hasattr(output_item, 'content'):
                    for content in output_item.content:
                        if hasattr(content, 'text'):
                            print(f"\n{content.text}")
        else:
            # Fallback: print the whole response
            print(f"\n{response}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error invoking agent: {e}")
        print(f"\nPossible issues:")
        print(f"  1. Agent deployment is not started")
        print(f"  2. Agent version doesn't exist")
        print(f"  3. Authentication failed")
        print(f"  4. Project endpoint is incorrect")


def interactive_mode():
    """Run in interactive mode for continuous conversation."""
    
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("Type your messages and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("="*60 + "\n")
    
    if not validate_config():
        return
    
    try:
        # Initialize once
        credential = DefaultAzureCredential()
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential
        )
        agent = client.agents.retrieve(agent_name=AGENT_NAME)
        openai_client = client.get_openai_client()
        
        print(f"✅ Connected to agent: {agent.name}\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nExiting...")
                break
            
            if not user_input:
                continue
            
            try:
                response = openai_client.responses.create(
                    input=[{"role": "user", "content": user_input}],
                    extra_body={
                        "agent": AgentReference(
                            name=agent.name,
                            version=AGENT_VERSION
                        ).as_dict()
                    }
                )
                
                print(f"\nAgent: ", end="")
                if hasattr(response, 'output_text'):
                    print(response.output_text)
                elif hasattr(response, 'output'):
                    print(response.output)
                else:
                    print(response)
                print()
                
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")


def main():
    """Main entry point."""
    
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--interactive", "-i"]:
            interactive_mode()
        elif sys.argv[1] in ["--help", "-h"]:
            print("Usage:")
            print("  python invoke_agent.py                    # Single test message")
            print("  python invoke_agent.py -i                 # Interactive mode")
            print('  python invoke_agent.py "Your message"     # Custom message')
            print("  python invoke_agent.py --help             # Show this help")
        else:
            # Use the provided message
            message = " ".join(sys.argv[1:])
            invoke_agent(message)
    else:
        # Default test message
        invoke_agent("Hello! What can you help me with?")


if __name__ == "__main__":
    main()
