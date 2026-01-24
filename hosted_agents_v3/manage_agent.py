#!/usr/bin/env python3
"""
Manage Hosted Agent Lifecycle

This script provides commands to manage the hosted agent:
- Start deployment
- Stop deployment
- Update agent
- Delete agent
- List agents
- Show agent details
"""

import os
import sys
import argparse
import subprocess
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ACCOUNT_NAME = os.getenv("AZURE_FOUNDRY_ACCOUNT_NAME")
PROJECT_NAME = os.getenv("AZURE_PROJECT_NAME")
AGENT_NAME = os.getenv("AGENT_NAME", "my-hosted-agent")
AGENT_VERSION = os.getenv("AGENT_VERSION", "1")


def validate_config() -> bool:
    """Validate required configuration."""
    
    errors = []
    if not ACCOUNT_NAME:
        errors.append("AZURE_FOUNDRY_ACCOUNT_NAME is not set")
    if not PROJECT_NAME:
        errors.append("AZURE_PROJECT_NAME is not set")
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


def run_az_command(args: list) -> bool:
    """
    Run an Azure CLI command.
    
    Args:
        args: List of command arguments
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        result = subprocess.run(
            ["az"] + args,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def start_agent(min_replicas: int = 1, max_replicas: int = 1):
    """Start the hosted agent deployment."""
    
    print(f"\nStarting agent: {AGENT_NAME} (version {AGENT_VERSION})")
    print(f"Replicas: min={min_replicas}, max={max_replicas}")
    
    args = [
        "cognitiveservices", "agent", "start",
        "--account-name", ACCOUNT_NAME,
        "--project-name", PROJECT_NAME,
        "--name", AGENT_NAME,
        "--agent-version", AGENT_VERSION,
        "--min-replicas", str(min_replicas),
        "--max-replicas", str(max_replicas)
    ]
    
    if run_az_command(args):
        print(f"\n✅ Agent started successfully!")
        print(f"Status will transition: Stopped → Starting → Started")
    else:
        print(f"\n❌ Failed to start agent")


def stop_agent():
    """Stop the hosted agent deployment."""
    
    print(f"\nStopping agent: {AGENT_NAME} (version {AGENT_VERSION})")
    
    args = [
        "cognitiveservices", "agent", "stop",
        "--account-name", ACCOUNT_NAME,
        "--project-name", PROJECT_NAME,
        "--name", AGENT_NAME,
        "--agent-version", AGENT_VERSION
    ]
    
    if run_az_command(args):
        print(f"\n✅ Agent stopped successfully!")
        print(f"Status will transition: Running → Stopping → Stopped")
    else:
        print(f"\n❌ Failed to stop agent")


def update_agent(min_replicas: Optional[int] = None, 
                 max_replicas: Optional[int] = None,
                 description: Optional[str] = None):
    """Update agent configuration (non-versioned update)."""
    
    print(f"\nUpdating agent: {AGENT_NAME} (version {AGENT_VERSION})")
    
    args = [
        "cognitiveservices", "agent", "update",
        "--account-name", ACCOUNT_NAME,
        "--project-name", PROJECT_NAME,
        "--name", AGENT_NAME,
        "--agent-version", AGENT_VERSION
    ]
    
    if min_replicas is not None:
        args.extend(["--min-replicas", str(min_replicas)])
    if max_replicas is not None:
        args.extend(["--max-replicas", str(max_replicas)])
    if description:
        args.extend(["--description", description])
    
    if run_az_command(args):
        print(f"\n✅ Agent updated successfully!")
    else:
        print(f"\n❌ Failed to update agent")


def delete_deployment():
    """Delete the agent deployment only (keeps the version)."""
    
    print(f"\nDeleting deployment: {AGENT_NAME} (version {AGENT_VERSION})")
    print("Note: This keeps the agent version for future use")
    
    args = [
        "cognitiveservices", "agent", "delete-deployment",
        "--account-name", ACCOUNT_NAME,
        "--project-name", PROJECT_NAME,
        "--name", AGENT_NAME,
        "--agent-version", AGENT_VERSION
    ]
    
    if run_az_command(args):
        print(f"\n✅ Deployment deleted successfully!")
    else:
        print(f"\n❌ Failed to delete deployment")


def delete_agent(version: Optional[str] = None):
    """Delete the agent (all versions or specific version)."""
    
    if version:
        print(f"\nDeleting agent version: {AGENT_NAME} (version {version})")
    else:
        print(f"\nDeleting all versions of agent: {AGENT_NAME}")
        print("⚠️  WARNING: This will delete ALL versions!")
    
    args = [
        "cognitiveservices", "agent", "delete",
        "--account-name", ACCOUNT_NAME,
        "--project-name", PROJECT_NAME,
        "--name", AGENT_NAME
    ]
    
    if version:
        args.extend(["--agent-version", version])
    
    if run_az_command(args):
        print(f"\n✅ Agent deleted successfully!")
    else:
        print(f"\n❌ Failed to delete agent")


def list_versions():
    """List all versions of the agent."""
    
    print(f"\nListing versions for agent: {AGENT_NAME}")
    
    args = [
        "cognitiveservices", "agent", "list-versions",
        "--account-name", ACCOUNT_NAME,
        "--project-name", PROJECT_NAME,
        "--name", AGENT_NAME
    ]
    
    run_az_command(args)


def show_details():
    """Show details of the agent."""
    
    print(f"\nShowing details for agent: {AGENT_NAME}")
    
    args = [
        "cognitiveservices", "agent", "show",
        "--account-name", ACCOUNT_NAME,
        "--project-name", PROJECT_NAME,
        "--name", AGENT_NAME
    ]
    
    run_az_command(args)


def main():
    """Main entry point with argument parsing."""
    
    parser = argparse.ArgumentParser(
        description="Manage Foundry Hosted Agent Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start agent with default settings
  python manage_agent.py start
  
  # Start with custom scaling
  python manage_agent.py start --min-replicas 1 --max-replicas 3
  
  # Stop agent
  python manage_agent.py stop
  
  # Update scaling
  python manage_agent.py update --min-replicas 2 --max-replicas 5
  
  # List all versions
  python manage_agent.py list
  
  # Show agent details
  python manage_agent.py show
  
  # Delete deployment only
  python manage_agent.py delete-deployment
  
  # Delete specific version
  python manage_agent.py delete --version 1
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start agent deployment")
    start_parser.add_argument("--min-replicas", type=int, default=1)
    start_parser.add_argument("--max-replicas", type=int, default=1)
    
    # Stop command
    subparsers.add_parser("stop", help="Stop agent deployment")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update agent configuration")
    update_parser.add_argument("--min-replicas", type=int)
    update_parser.add_argument("--max-replicas", type=int)
    update_parser.add_argument("--description", type=str)
    
    # Delete deployment command
    subparsers.add_parser("delete-deployment", help="Delete deployment (keep version)")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete agent version(s)")
    delete_parser.add_argument("--version", type=str, help="Specific version to delete")
    
    # List command
    subparsers.add_parser("list", help="List all agent versions")
    
    # Show command
    subparsers.add_parser("show", help="Show agent details")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Validate configuration
    if not validate_config():
        return 1
    
    # Execute command
    if args.command == "start":
        start_agent(args.min_replicas, args.max_replicas)
    elif args.command == "stop":
        stop_agent()
    elif args.command == "update":
        update_agent(args.min_replicas, args.max_replicas, args.description)
    elif args.command == "delete-deployment":
        delete_deployment()
    elif args.command == "delete":
        delete_agent(args.version)
    elif args.command == "list":
        list_versions()
    elif args.command == "show":
        show_details()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
