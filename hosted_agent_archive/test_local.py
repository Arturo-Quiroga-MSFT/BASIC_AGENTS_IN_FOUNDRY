"""
Local testing script for the weather agent.
Tests the weather function directly without requiring Azure authentication.
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from weather_functions import execute_function

# Load environment variables from .env file
load_dotenv()

async def test_weather():
    """Test weather function locally."""
    
    test_cities = [
        "Mexico City",
        "Toronto",
        "London",
        "Tokyo"
    ]
    
    print("=" * 60)
    print("Testing Weather Agent Locally")
    print("=" * 60)
    print()
    
    for city in test_cities:
        print(f"Testing weather for: {city}")
        print("-" * 60)
        
        try:
            # Call the weather function
            result = await execute_function(
                "get_real_weather",
                {"location": city}
            )
            
            # Display result (it's already a formatted string)
            if "Error" in result or "Sorry" in result:
                print(f"❌ {result}")
            else:
                print(f"✅ {result}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()
    
    print("=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_weather())
