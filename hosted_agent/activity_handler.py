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
        self.conversations = {}  # Store active conversations by user ID
        
    async def initialize(self):
        """Initialize Azure AI clients."""
        try:
            self.credential = DefaultAzureCredential()
            self.project_client = AIProjectClient(
                endpoint=self.endpoint,
                credential=self.credential
            )
            self.openai_client = self.project_client.get_openai_client()
            logger.info("Azure AI clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI clients: {e}")
            raise
    
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
            conversation_id = activity.get("conversation", {}).get("id")
            
            logger.info(f"Message from user {user_id}: {user_message}")
            
            # Get or create conversation for this user
            if user_id not in self.conversations:
                conversation = await self._create_conversation(user_id)
                self.conversations[user_id] = conversation.id
            else:
                # Add message to existing conversation
                await self.openai_client.conversations.items.create(
                    conversation_id=self.conversations[user_id],
                    items=[{
                        "type": "message",
                        "role": "user",
                        "content": user_message
                    }]
                )
            
            # Get agent response
            response_text = await self._get_agent_response(
                self.conversations[user_id],
                user_message
            )
            
            return self._create_response(activity, response_text)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return self._create_response(
                activity,
                "Sorry, I encountered an error processing your request."
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
    
    async def _create_conversation(self, user_id: str) -> Any:
        """Create a new conversation for a user."""
        logger.info(f"Creating new conversation for user: {user_id}")
        conversation = await self.openai_client.conversations.create(
            items=[{
                "type": "message",
                "role": "system",
                "content": (
                    f"You are {Config.AGENT_NAME}, a helpful weather assistant. "
                    "Provide real-time weather information using the get_real_weather function. "
                    "Be conversational and helpful."
                )
            }]
        )
        return conversation
    
    async def _get_agent_response(
        self,
        conversation_id: str,
        user_message: str
    ) -> str:
        """
        Get agent response using the Foundry agent.
        
        Args:
            conversation_id: Conversation ID
            user_message: User's message
            
        Returns:
            Agent response text
        """
        try:
            # Create response with agent reference
            response = await self.openai_client.responses.create(
                conversation=conversation_id,
                extra_body={
                    "agent": {
                        "name": Config.AGENT_NAME,
                        "version": Config.AGENT_VERSION,
                        "type": "agent_reference"
                    }
                },
                input=""
            )
            
            # Handle function calls
            if response.output:
                for item in response.output:
                    if item.type == "function_call":
                        logger.info(f"Executing function: {item.name}")
                        
                        # Execute the function
                        args = json.loads(item.arguments)
                        result = await execute_function(item.name, args)
                        logger.info(f"Function result: {result[:100]}...")
                        
                        # Submit function result back
                        response = await self.openai_client.responses.create(
                            conversation=conversation_id,
                            extra_body={
                                "agent": {
                                    "name": Config.AGENT_NAME,
                                    "version": Config.AGENT_VERSION,
                                    "type": "agent_reference"
                                }
                            },
                            input=[{
                                "type": "function_call_output",
                                "call_id": item.call_id,
                                "output": result
                            }]
                        )
            
            return response.output_text or "Sorry, I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
            raise
    
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
            await self.project_client.close()
        if self.credential:
            await self.credential.close()
        logger.info("Activity handler cleaned up")
