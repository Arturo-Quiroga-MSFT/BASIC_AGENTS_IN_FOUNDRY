"""
Foundry Agent with A2A Tool

Creates a Foundry agent that calls an external A2A-compliant agent.
The Foundry agent keeps control and summarizes the external agent's response.
"""
import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import A2ATool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


def main():
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"]
    a2a_conn_name = os.environ["A2A_PROJECT_CONNECTION_NAME"]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        # Get A2A connection
        a2a_connection = project_client.connections.get(a2a_conn_name)
        print(f"Using A2A connection: {a2a_connection.name}")

        # Create A2A tool
        tool = A2ATool(project_connection_id=a2a_connection.id)

        # Create agent with A2A tool
        agent = project_client.agents.create_version(
            agent_name="A2A_Explorer",
            definition=PromptAgentDefinition(
                model=model,
                instructions=(
                    "You are a helpful assistant. When the user asks a question, "
                    "use the A2A tool to query the connected agent and summarize "
                    "the response for the user."
                ),
                tools=[tool],
            ),
        )
        print(f"Agent created: {agent.name} (v{agent.version})")

        # Interactive loop
        try:
            while True:
                user_input = input("\nYou: ").strip()
                if not user_input or user_input.lower() in ("quit", "exit"):
                    break

                print("\nAgent: ", end="", flush=True)
                stream = openai_client.responses.create(
                    stream=True,
                    tool_choice="required",
                    input=user_input,
                    extra_body={
                        "agent": {"name": agent.name, "type": "agent_reference"}
                    },
                )

                for event in stream:
                    if event.type == "response.output_text.delta":
                        print(event.delta, end="", flush=True)
                    elif event.type == "response.completed":
                        print()  # newline after streaming

        except KeyboardInterrupt:
            print("\n\nInterrupted.")

        finally:
            print("\nCleaning up...")
            project_client.agents.delete_version(
                agent_name=agent.name, agent_version=agent.version
            )
            print("Agent deleted.")


if __name__ == "__main__":
    main()
