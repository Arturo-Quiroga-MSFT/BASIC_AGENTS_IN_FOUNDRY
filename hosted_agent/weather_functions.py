"""
Weather function implementations for hosted agent.
"""

import os
import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def get_real_weather(location: str) -> str:
    """
    Get real-time weather information for a location using OpenWeatherMap API.
    
    Args:
        location: The city name or location to get weather for
        
    Returns:
        A formatted string with current weather information
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        logger.error("OPENWEATHER_API_KEY not configured")
        return "Error: Weather API key not configured"
    
    try:
        async with httpx.AsyncClient() as client:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"
            }
            
            logger.info(f"Fetching weather for: {location}")
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Extract weather information
            temp_c = data["main"]["temp"]
            temp_f = (temp_c * 9/5) + 32
            feels_like_c = data["main"]["feels_like"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            city = data["name"]
            country = data["sys"]["country"]
            
            # Format response
            result = (
                f"Weather in {city}, {country}: "
                f"{temp_c:.1f}°C ({temp_f:.1f}°F), {description}. "
                f"Feels like {feels_like_c:.1f}°C. "
                f"Humidity: {humidity}%, Wind: {wind_speed} m/s"
            )
            
            logger.info(f"Weather retrieved successfully for {city}")
            return result
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching weather: {e}")
        if e.response.status_code == 404:
            return f"Sorry, I couldn't find weather information for '{location}'. Please check the city name."
        return f"Error fetching weather data: HTTP {e.response.status_code}"
    except httpx.TimeoutException:
        logger.error("Timeout fetching weather")
        return "Sorry, the weather service is taking too long to respond. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error fetching weather: {e}")
        return f"Sorry, I encountered an error fetching the weather: {str(e)}"


# Function registry for the agent
WEATHER_FUNCTIONS = {
    "get_real_weather": {
        "function": get_real_weather,
        "definition": {
            "type": "function",
            "name": "get_real_weather",
            "description": "Get real-time weather information for a city using OpenWeatherMap API",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name or location (e.g., 'Seattle', 'London', 'Tokyo')"
                    }
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    }
}


async def execute_function(function_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a weather function by name.
    
    Args:
        function_name: Name of the function to execute
        arguments: Dictionary of arguments to pass to the function
        
    Returns:
        Function result as string
    """
    if function_name not in WEATHER_FUNCTIONS:
        logger.error(f"Unknown function: {function_name}")
        return f"Error: Unknown function '{function_name}'"
    
    try:
        func = WEATHER_FUNCTIONS[function_name]["function"]
        result = await func(**arguments)
        return result
    except Exception as e:
        logger.error(f"Error executing function {function_name}: {e}")
        return f"Error executing function: {str(e)}"


def get_function_definitions() -> list:
    """
    Get all function definitions for the agent.
    
    Returns:
        List of function definitions
    """
    return [func["definition"] for func in WEATHER_FUNCTIONS.values()]
