"""Register a hosted agent version in Azure AI Foundry.

Requires:
  AZURE_AI_PROJECT_ENDPOINT (new project endpoint)
  ACR_IMAGE (full ACR image URL, e.g., aqr2d2acr001.azurecr.io/weatheragent:v2)
  AGENT_NAME (default: WeatherAgent)
  OPENWEATHER_API_KEY (optional, for container env)
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition, ProtocolVersionRecord, AgentProtocol


def main() -> None:
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    image = os.environ.get("ACR_IMAGE", "")
    agent_name = os.environ.get("AGENT_NAME", "WeatherAgent")
    openweather = os.environ.get("OPENWEATHER_API_KEY", "")

    if not image:
        raise ValueError("ACR_IMAGE is required (e.g., aqr2d2acr001.azurecr.io/weatheragent:v2)")

    env_vars = {
        "AZURE_AI_PROJECT_ENDPOINT": endpoint,
        "PORT": "8088",
        "LOG_LEVEL": "INFO",
        "AGENT_NAME": agent_name,
        "AGENT_VERSION": "2",
    }

    if openweather:
        env_vars["OPENWEATHER_API_KEY"] = openweather

    definition = ImageBasedHostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="v1")
        ],
        cpu="1",
        memory="2Gi",
        image=image,
        environment_variables=env_vars,
    )

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as client,
    ):
        agent = client.agents.create_version(
            agent_name=agent_name,
            description="Weather agent (hosted)",
            definition=definition,
        )

    print("Hosted agent version created:")
    print(f"  Name: {agent.name}")
    print(f"  Version: {agent.version}")


if __name__ == "__main__":
    main()
