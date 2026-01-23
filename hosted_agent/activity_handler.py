"""
Activity Protocol handler for Bot Service integration.

This module handles Activity Protocol messages from Azure Bot Service,
which acts as a relay between Microsoft 365 and the hosted agent.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool

from config import Config
from weather_functions import execute_function, get_function_definitions

logger = logging.getLogger(__name__)


class ActivityHandler:
    """Handles Activity Protocol messages."""
    
    def __init__(self):
        """Initialize the activity handler."""
        self.endpoint = Config.AZURE_AI_PROJECT_ENDPOINT
        self.credential = None
        self.project_client = None
        self.openai_client = None
        self.conversations = {}  # Store conversation IDs by user
        
    async def initialize(self):
        """Initialize Azure AI clients."""
        try:
            self.credential = DefaultAzureCredential()
            self.project_client = AIProjectClient(
                endpoint=self.endpoint,
                credential=self.credential
            )
            self.openai_client = self.project_client.get_openai_client()
            logger.info(f"Azure AI clients initialized successfully")
        except Exception as e:
            logger.warning(
                "Azure AI client init failed; continuing without it. Error: %s",
                e
            )
            self.credential = None
            self.project_client = None
            self.openai_client = None
    
    async def handle_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming Activity Protocol message.
        
        Args:
            activity: Activity object from Bot Service
            
        Returns:
            Response activity
        """
        activity_type = activity.get("type", "")
        logger.info(f"Received activity type: {activity_type}")
        
        if activity_type == "message":
            return await self._handle_message(activity)
        elif activity_type == "conversationUpdate":
            return await self._handle_conversation_update(activity)
        else:
            logger.warning(f"Unsupported activity type: {activity_type}")
            return self._create_response(activity, "Activity type not supported")
    
    async def _handle_message(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a message activity."""
        try:
            user_id = activity.get("from", {}).get("id", "unknown")
            user_message = activity.get("text", "")
            
            logger.info(f"Message from user {user_id}: {user_message}")
            
            response_text = await self.generate_reply(user_message, user_id)
            
            return self._create_response(activity, response_text)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return self._create_response(
                activity,
                "Sorry, I encountered an error processing your request."
            )

    async def generate_reply(self, user_message: str, user_id: str = "unknown") -> str:
        """Generate a text reply for a user message."""
        # Simple pattern matching for weather queries
        # Extract city name from message
        import re
        match = re.search(r"weather in ([A-Za-z\s]+)", user_message, re.IGNORECASE)

        if match:
            city = match.group(1).strip()
            logger.info(f"Extracted city: {city}")

            # Call weather function directly
            result = await execute_function("get_real_weather", {"location": city})
            logger.info(f"Weather result: {result[:100]}...")

            return result

        return (
            f"I'm {Config.AGENT_NAME}, your weather assistant! "
            "Ask me about the weather in any city, like 'What is the weather in Tokyo?'"
        )
    
    async def _handle_conversation_update(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a conversation update activity (user joins/leaves)."""
        members_added = activity.get("membersAdded", [])
        
        for member in members_added:
            if member.get("id") != activity.get("recipient", {}).get("id"):
                # User joined, send welcome message
                welcome_text = (
                    f"👋 Hello! I'm {Config.AGENT_NAME}, your weather assistant. "
                    "Ask me about the weather in any city!"
                )
                return self._create_response(activity, welcome_text)
        
        return {"type": "message", "text": ""}
    
    def _create_response(self, activity: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Create a response activity."""
        return {
            "type": "message",
            "from": activity.get("recipient"),
            "conversation": activity.get("conversation"),
            "recipient": activity.get("from"),
            "text": text,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.project_client:
            self.project_client.close()
        if self.credential:
            self.credential.close()
        logger.info("Activity handler cleaned up")

