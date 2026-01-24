#!/usr/bin/env python3
"""
Create Hosted Agent Version using Azure Foundry SDK

This script creates a hosted agent version in Microsoft Foundry using the
Azure AI Projects SDK, following the official documentation.

Prerequisites:
1. Azure Container Registry with the agent image
2. Proper RBAC permissions configured on ACR
3. Account-level capability host created
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ImageBasedHostedAgentDefinition,
    ProtocolVersionRecord,
    AgentProtocol
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME", "my-hosted-agent")
CONTAINER_IMAGE = os.getenv("CONTAINER_IMAGE")  # e.g., myregistry.azurecr.io/myagent:v1
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")


def validate_configuration():
    """Validate that all required configuration is present."""
    
    errors = []
    
    if not PROJECT_ENDPOINT:
        errors.append("AZURE_AI_PROJECT_ENDPOINT is not set")
    
    if not CONTAINER_IMAGE:
        errors.append("CONTAINER_IMAGE is not set (e.g., myregistry.azurecr.io/myagent:v1)")
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease set these in your .env file or environment variables.")
        return False
    
    return True


def create_hosted_agent_version():
    """
    Create a hosted agent version in Microsoft Foundry.
    
    This function:
    1. Authenticates to Azure
    2. Creates an AI Project client
    3. Registers the containerized agent
    4. Returns the created agent information
    """
    
    print("="*60)
    print("CREATE HOSTED AGENT VERSION")
    print("="*60)
    
    # Validate configuration
    if not validate_configuration():
        return None
    
    print(f"\nConfiguration:")
    print(f"  Project Endpoint: {PROJECT_ENDPOINT}")
    print(f"  Agent Name: {AGENT_NAME}")
    print(f"  Container Image: {CONTAINER_IMAGE}")
    print(f"  Model Name: {MODEL_NAME}")
    
    try:
        print("\n1. Authenticating to Azure...")
        credential = DefaultAzureCredential()
        
        print("2. Creating AI Project client...")
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential
        )
        
        print("3. Creating hosted agent version...")
        
        # Create the agent from a container image
        agent = client.agents.create_version(
            agent_name=AGENT_NAME,
            definition=ImageBasedHostedAgentDefinition(
                # Protocol version for the agent
                container_protocol_versions=[
                    ProtocolVersionRecord(
                        protocol=AgentProtocol.RESPONSES,
                        version="v1"
                    )
                ],
                
                # Resource allocation
                cpu="1",           # 1 CPU core
                memory="2Gi",      # 2 GB memory
                
                # Container image from ACR
                image=CONTAINER_IMAGE,
                
                # Environment variables passed to the container
                environment_variables={
                    "AZURE_AI_PROJECT_ENDPOINT": PROJECT_ENDPOINT,
                    "MODEL_NAME": MODEL_NAME,
                    "CUSTOM_SETTING": "value"
                }
            )
        )
        
        print("\n✅ Hosted agent version created successfully!")
        print(f"\nAgent Details:")
        print(f"  Name: {agent.name}")
        print(f"  Version: {agent.version if hasattr(agent, 'version') else 'N/A'}")
        print(f"  ID: {agent.id if hasattr(agent, 'id') else 'N/A'}")
        
        print(f"\nNext Steps:")
        print(f"1. Start the agent deployment using:")
        print(f"   az cognitiveservices agent start \\")
        print(f"     --account-name <account-name> \\")
        print(f"     --project-name <project-name> \\")
        print(f"     --name {AGENT_NAME} \\")
        print(f"     --agent-version <version>")
        print(f"\n2. Or use the manage_agent.py script")
        
        return agent
        
    except Exception as e:
        print(f"\n❌ Error creating hosted agent: {e}")
        print(f"\nPossible issues:")
        print(f"  1. Check that the container image exists in ACR")
        print(f"  2. Verify ACR permissions are configured correctly")
        print(f"  3. Ensure the capability host is created")
        print(f"  4. Verify you have proper RBAC roles")
        return None


def main():
    """Main entry point."""
    
    result = create_hosted_agent_version()
    
    if result:
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("FAILED")
        print("="*60)
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
