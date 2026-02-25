"""
Verify A2A Connection in Foundry Project

Run this first to confirm your credentials and A2A connection are configured correctly.
"""
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


def main():
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    connection_name = os.environ.get("A2A_PROJECT_CONNECTION_NAME")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        print(f"✓ Connected to project: {endpoint}")

        if connection_name:
            try:
                conn = project_client.connections.get(connection_name)
                print(f"✓ A2A connection verified: {conn.name}")
                print(f"  Type: {conn.type}")
            except Exception as e:
                print(f"✗ A2A connection '{connection_name}' not found: {e}")
        else:
            print("A2A_PROJECT_CONNECTION_NAME not set. Available connections:")
            for conn in project_client.connections.list():
                print(f"  - {conn.name} ({conn.type})")


if __name__ == "__main__":
    main()
