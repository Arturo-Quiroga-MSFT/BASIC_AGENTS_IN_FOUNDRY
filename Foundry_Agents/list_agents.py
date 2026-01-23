# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    List all agents in Azure AI Foundry project.

USAGE:
    python list_agents.py

    Before running:
    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set environment variable:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv(Path(__file__).parent / ".env")

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        print("🔍 Fetching agents from Azure AI Foundry...\n")
        
        # List all agents
        agents = project_client.agents.list()
        
        agent_count = 0
        for agent in agents:
            agent_count += 1
            print(f"{'='*60}")
            print(f"Agent #{agent_count}")
            print(f"{'='*60}")
            print(f"  📋 Name:        {agent.name}")
            print(f"  🆔 ID:          {agent.id}")
            
            # Get latest version details (versions supports dict-like access)
            if hasattr(agent, 'versions') and agent.versions and 'latest' in agent.versions:
                latest = agent.versions['latest']
                print(f"  📦 Version:     {latest.get('version', 'N/A')}")
                
                if 'definition' in latest:
                    definition = latest['definition']
                    
                    # Show kind (prompt vs workflow)
                    if 'kind' in definition:
                        print(f"  📑 Type:        {definition['kind']}")
                    
                    if 'model' in definition:
                        print(f"  🤖 Model:       {definition['model']}")
                    
                    # Show tools with names
                    if 'tools' in definition and definition['tools']:
                        tools = definition['tools']
                        print(f"  🔧 Tools:       {len(tools)} tool(s)")
                        for tool in tools[:3]:  # Show first 3 tools
                            tool_type = tool.get('type', 'unknown')
                            if tool_type == 'function':
                                print(f"                  - {tool.get('name', 'unnamed')} (function)")
                            else:
                                print(f"                  - {tool_type}")
                        if len(tools) > 3:
                            print(f"                  ... and {len(tools) - 3} more")
                    
                    # Show instructions preview
                    if 'instructions' in definition and definition['instructions']:
                        instructions = definition['instructions'].strip()
                        preview = instructions[:80].replace('\n', ' ') + "..." if len(instructions) > 80 else instructions
                        print(f"  📖 Instructions: {preview}")
                
                if 'description' in latest and latest['description']:
                    print(f"  📝 Description: {latest['description']}")
                
                if 'created_at' in latest:
                    from datetime import datetime
                    created = datetime.fromtimestamp(latest['created_at'])
                    print(f"  📅 Created:     {created.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print()
        
        if agent_count == 0:
            print("No agents found in this project.")
        else:
            print(f"\n✅ Total agents: {agent_count}")


if __name__ == "__main__":
    main()
