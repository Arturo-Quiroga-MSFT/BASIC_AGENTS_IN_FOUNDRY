"""
WeatherAgent using Azure AI Agent Server Core package.
Following official hosted agents pattern from:
https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents
"""

import os
import datetime
import logging
import httpx
from typing import AsyncIterable
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from azure.ai.agentserver.core import FoundryCBAgent
from azure.ai.agentserver.core.models import CreateResponse, Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    ResponsesAssistantMessageItemResource,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_weather(location: str) -> str:
    """Get real-time weather information for a location."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: Weather API key not configured"
    
    try:
        async with httpx.AsyncClient() as client:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {"q": location, "appid": api_key, "units": "metric"}
            
            logger.info(f"Fetching weather for: {location}")
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            temp_c = data["main"]["temp"]
            temp_f = (temp_c * 9/5) + 32
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            city = data["name"]
            country = data["sys"]["country"]
            
            return (
                f"Weather in {city}, {country}: "
                f"{temp_c:.1f}°C ({temp_f:.1f}°F), {description}. "
                f"Humidity: {humidity}%"
            )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Sorry, I couldn't find weather information for '{location}'"
        return f"Error fetching weather data: HTTP {e.response.status_code}"
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return f"Error: {str(e)}"


def stream_weather_response(text: str) -> AsyncIterable:
    """Stream text response with delta events."""
    assembled = ""
    for i, token in enumerate(text.split(" ")):
        piece = token if i == len(text.split(" ")) - 1 else token + " "
        assembled += piece
        yield ResponseTextDeltaEvent(delta=piece)
    yield ResponseTextDoneEvent(text=assembled)


async def agent_run(request_body):
    """
    Main agent logic following Foundry Responses protocol.
    
    Extracts user message, processes weather queries, returns response.
    """
    logger.info(f"Agent run started")
    
    # Extract user message from the request object
    user_message = ""
    
    # The request_body is AgentRunContext, the request property contains the actual request dict
    if hasattr(request_body, 'request') and isinstance(request_body.request, dict):
        req = request_body.request
        messages = req.get('messages', [])
        for msg in messages:
            if isinstance(msg, dict) and msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
    
    logger.info(f"User message extracted: {user_message}")
    
    # Simple pattern matching for weather queries
    import re
    match = re.search(r'weather (?:in|for) ([A-Za-z\s]+)', user_message, re.IGNORECASE)
    
    if match:
        city = match.group(1).strip()
        response_text = await get_weather(city)
    else:
        response_text = (
            "I'm a weather assistant! Ask me about the weather in any city, "
            "like 'What is the weather in Tokyo?'"
        )
    
    # Handle streaming response
    if request_body.stream:
        return stream_weather_response(response_text)
    
    # Non-streaming response
    output_content = [
        ItemContentOutputText(
            text=response_text,
            annotations=[],
        )
    ]
    
    response = OpenAIResponse(
        metadata={},
        temperature=0.0,
        top_p=0.0,
        user="user",
        id=f"resp_{datetime.datetime.now().timestamp()}",
        created_at=datetime.datetime.now(),
        output=[
            ResponsesAssistantMessageItemResource(
                status="completed",
                content=output_content,
            )
        ],
    )
    return response


# Create agent instance using FoundryCBAgent
my_agent = FoundryCBAgent()
my_agent.agent_run = agent_run


if __name__ == "__main__":
    # IMPORTANT:
    # FoundryCBAgent defaults to env var DEFAULT_AD_PORT (fallback 8088) and does NOT
    # read the common platform env var PORT. Many hosted container platforms probe PORT.
    # So we honor PORT first, then DEFAULT_AD_PORT, then 8088.
    port_str = os.getenv("PORT") or os.getenv("DEFAULT_AD_PORT") or "8088"
    my_agent.run(port=int(port_str))
