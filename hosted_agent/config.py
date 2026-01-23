"""
Configuration management for hosted WeatherAgent.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration for hosted agent."""
    
    # Server settings
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Agent settings
    AGENT_NAME: str = os.getenv("AGENT_NAME", "WeatherAgent")
    AGENT_VERSION: str = os.getenv("AGENT_VERSION", "2")
    AGENT_DESCRIPTION: str = os.getenv(
        "AGENT_DESCRIPTION",
        "Weather agent with real OpenWeatherMap API integration"
    )
    
    # Azure settings
    AZURE_AI_PROJECT_ENDPOINT: str = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
    
    # API Keys
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    
    # Application Insights (optional)
    APPLICATIONINSIGHTS_CONNECTION_STRING: Optional[str] = os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING"
    )
    
    # Bot Service authentication
    MICROSOFT_APP_ID: Optional[str] = os.getenv("MICROSOFT_APP_ID")
    MICROSOFT_APP_PASSWORD: Optional[str] = os.getenv("MICROSOFT_APP_PASSWORD")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        errors = []
        
        if not cls.AZURE_AI_PROJECT_ENDPOINT:
            errors.append("AZURE_AI_PROJECT_ENDPOINT is required")
        
        if not cls.OPENWEATHER_API_KEY:
            errors.append("OPENWEATHER_API_KEY is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    @classmethod
    def to_dict(cls) -> dict:
        """Export configuration as dictionary (excluding secrets)."""
        return {
            "port": cls.PORT,
            "host": cls.HOST,
            "log_level": cls.LOG_LEVEL,
            "agent_name": cls.AGENT_NAME,
            "agent_version": cls.AGENT_VERSION,
            "agent_description": cls.AGENT_DESCRIPTION,
            "azure_endpoint_configured": bool(cls.AZURE_AI_PROJECT_ENDPOINT),
            "openweather_key_configured": bool(cls.OPENWEATHER_API_KEY),
            "app_insights_configured": bool(cls.APPLICATIONINSIGHTS_CONNECTION_STRING),
            "bot_auth_configured": bool(cls.MICROSOFT_APP_ID and cls.MICROSOFT_APP_PASSWORD),
        }
