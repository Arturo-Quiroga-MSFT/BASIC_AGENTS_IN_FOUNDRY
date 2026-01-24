#!/usr/bin/env python3
"""
Local Testing Script for Hosted Agent

Tests the agent running locally via the hosting adapter's HTTP endpoint.
Based on the REST API testing approach from Microsoft documentation.
"""

import requests
import json
import time
from typing import Dict, Any


# Configuration
BASE_URL = "http://localhost:8088"
RESPONSES_ENDPOINT = f"{BASE_URL}/responses"


def test_agent(message: str) -> Dict[str, Any]:
    """
    Send a message to the locally running agent and get the response.
    
    Args:
        message: The user message to send
        
    Returns:
        The full response from the agent
    """
    
    # OpenAI Responses API format
    payload = {
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*60}")
    print(f"Sending message: {message}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            RESPONSES_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"\nStatus Code: {response.status_code}")
        
        # Extract and display the agent's message from output array
        if "output" in result and len(result["output"]) > 0:
            for output_item in result["output"]:
                if output_item.get("type") == "message" and output_item.get("role") == "assistant":
                    content_items = output_item.get("content", [])
                    for content in content_items:
                        if content.get("type") == "output_text":
                            print(f"\n✅ Agent Response:")
                            print(f"   {content.get('text', 'No text')}")
        else:
            # Fallback: show full response if format is unexpected
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the agent.")
        print("Make sure the agent is running: python agent.py")
        return {}
    
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out.")
        return {}
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return {}


def check_health() -> bool:
    """Check if the agent server is running."""
    
    print("Checking agent availability...")
    
    try:
        # Try to connect to the base URL
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Agent server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.RequestException:
        print("❌ Agent server is not running")
        print("Start the agent with: python agent.py")
        return False


def run_test_suite():
    """Run a suite of test messages."""
    
    print("\n" + "="*60)
    print("HOSTED AGENT LOCAL TEST SUITE")
    print("="*60)
    
    # Check if server is running
    if not check_health():
        return
    
    # Test cases
    test_cases = [
        "Hello! What can you help me with?",
        "What is Microsoft Foundry?",
        "Explain what a hosted agent is.",
        "Tell me about your capabilities.",
    ]
    
    results = []
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n\n{'#'*60}")
        print(f"TEST {i} of {len(test_cases)}")
        print(f"{'#'*60}")
        
        result = test_agent(test_message)
        results.append({
            "test": i,
            "message": test_message,
            "success": bool(result),
            "response": result
        })
        
        # Brief pause between tests
        if i < len(test_cases):
            time.sleep(2)
    
    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"Tests Passed: {successful}/{total}")
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} Test {result['test']}: {result['message'][:50]}...")
    
    print("\n" + "="*60)


def interactive_mode():
    """Run the agent in interactive mode for manual testing."""
    
    print("\n" + "="*60)
    print("INTERACTIVE TEST MODE")
    print("="*60)
    print("Type your messages and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("="*60 + "\n")
    
    if not check_health():
        return
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nExiting interactive mode...")
                break
            
            if not user_input:
                continue
            
            test_agent(user_input)
            
        except KeyboardInterrupt:
            print("\n\nExiting interactive mode...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point for testing."""
    
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            interactive_mode()
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage:")
            print("  python test_local.py              # Run test suite")
            print("  python test_local.py -i           # Interactive mode")
            print("  python test_local.py --help       # Show this help")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        run_test_suite()


if __name__ == "__main__":
    main()
