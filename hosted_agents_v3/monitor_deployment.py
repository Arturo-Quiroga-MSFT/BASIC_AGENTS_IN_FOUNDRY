#!/usr/bin/env python3
"""
Monitor agent deployment status until it's running or fails.
"""
import os
import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_NAME = "r2d2-hosted-agents-project-resou"
PROJECT_NAME = "r2d2-hosted-agents-project"
AGENT_NAME = "my-hosted-agent"
AGENT_VERSION = "2"

def check_status():
    """Check current agent status."""
    try:
        result = subprocess.run(
            [
                "az", "cognitiveservices", "agent", "start",
                "--account-name", ACCOUNT_NAME,
                "--project-name", PROJECT_NAME,
                "--name", AGENT_NAME,
                "--agent-version", AGENT_VERSION,
                "--output", "json"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        data = json.loads(result.stdout)
        return data.get("Status", "Unknown")
    except Exception as e:
        print(f"Error checking status: {e}")
        return None

def main():
    print(f"🔍 Monitoring agent deployment: {AGENT_NAME} version {AGENT_VERSION}")
    print(f"=" * 70)
    
    start_time = time.time()
    check_count = 0
    
    while True:
        check_count += 1
        elapsed = int(time.time() - start_time)
        
        status = check_status()
        
        print(f"[{elapsed:03d}s] Check #{check_count}: Status = {status}")
        
        if status == "Started":
            print(f"\n✅ Agent is RUNNING! (took {elapsed} seconds)")
            print(f"\n📝 Test the agent with:")
            print(f"   python invoke_agent.py")
            break
        elif status == "Failed":
            print(f"\n❌ Agent deployment FAILED! (after {elapsed} seconds)")
            print(f"\n📝 Check the portal for detailed error logs:")
            print(f"   https://ai.azure.com/build/agent/{AGENT_NAME}")
            break
        elif status in ["InProgress", "Starting"]:
            # Still starting - wait and check again
            if elapsed > 600:  # 10 minutes timeout
                print(f"\n⚠️  Deployment taking too long (>{elapsed}s). Check portal for issues.")
                break
            time.sleep(10)  # Check every 10 seconds
        else:
            print(f"\n⚠️  Unexpected status: {status}")
            time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
