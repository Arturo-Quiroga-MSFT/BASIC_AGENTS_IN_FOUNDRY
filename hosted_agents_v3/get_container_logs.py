#!/usr/bin/env python3
"""
Get container logs for a hosted agent deployment to troubleshoot startup issues.
Based on official Microsoft documentation:
https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry#view-container-log-stream
"""
import os
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "AQ-FOUNDRY-RG")
ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME", "r2d2-hosted-agents-project-resou")
AGENT_NAME = os.getenv("AGENT_NAME", "my-hosted-agent")
AGENT_VERSION = "1"

def get_access_token():
    """Get Azure access token for authentication."""
    try:
        result = subprocess.run(
            ["az", "account", "get-access-token", "--query", "accessToken", "-o", "tsv"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting access token: {e}")
        print(f"stderr: {e.stderr}")
        return None

def get_container_logs(log_kind="console", tail=100):
    """
    Fetch container logs for the hosted agent.
    
    Args:
        log_kind: "console" for stdout/stderr or "system" for container app events
        tail: Number of trailing lines to return (1-300)
    """
    print(f"\n{'='*70}")
    print(f"Fetching {log_kind} logs for agent: {AGENT_NAME} version {AGENT_VERSION}")
    print(f"{'='*70}\n")
    
    # Get access token
    token = get_access_token()
    if not token:
        print("Failed to get access token")
        return
    
    # Try with CognitiveServices provider
    url = (
        f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}"
        f"/resourceGroups/{RESOURCE_GROUP}"
        f"/providers/Microsoft.CognitiveServices/accounts/{ACCOUNT_NAME}"
        f"/agents/{AGENT_NAME}/versions/{AGENT_VERSION}"
        f"/containers/default:logstream"
        f"?kind={log_kind}&tail={tail}&api-version=2025-10-01-preview"
    )
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/plain"
    }
    
    print(f"Request URL: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        
        if response.status_code == 200:
            print(f"✅ Successfully retrieved {log_kind} logs:\n")
            print("-" * 70)
            for line in response.iter_lines():
                if line:
                    print(line.decode('utf-8'))
            print("-" * 70)
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
            # Try alternate approach using az rest
            print("\n\nTrying alternate approach with az rest...\n")
            try_az_rest(log_kind, tail)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        print("\n\nTrying alternate approach with az rest...\n")
        try_az_rest(log_kind, tail)

def try_az_rest(log_kind="console", tail=100):
    """Try fetching logs using az rest command."""
    # Try with the exact path from the documentation but adjusted for CognitiveServices
    url_path = (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        f"/resourceGroups/{RESOURCE_GROUP}"
        f"/providers/Microsoft.CognitiveServices/accounts/{ACCOUNT_NAME}"
        f"/projects/r2d2-hosted-agents-project"  # Add project name
        f"/agents/{AGENT_NAME}/versions/{AGENT_VERSION}"
        f"/containers/default:logstream"
        f"?kind={log_kind}&tail={tail}&api-version=2025-10-01-preview"
    )
    
    full_url = f"https://management.azure.com{url_path}"
    
    try:
        result = subprocess.run(
            ["az", "rest", "--method", "GET", "--url", full_url],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Logs retrieved via az rest:")
            print("-" * 70)
            print(result.stdout)
            print("-" * 70)
        else:
            print(f"❌ az rest failed with exit code {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
    except Exception as e:
        print(f"❌ az rest command failed: {e}")

def main():
    print("\n🔍 Hosted Agent Container Log Viewer")
    print("=" * 70)
    
    # Fetch console logs (stdout/stderr from the container)
    get_container_logs(log_kind="console", tail=100)
    
    # Optionally fetch system logs (container app events)
    print("\n" * 2)
    user_input = input("Do you want to see system event logs too? (y/n): ")
    if user_input.lower() == 'y':
        get_container_logs(log_kind="system", tail=50)
    
    print("\n✅ Log retrieval complete")
    print("\n💡 Look for error messages in the logs above to diagnose the deployment issue")

if __name__ == "__main__":
    main()
