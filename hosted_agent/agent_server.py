"""
Hosted WeatherAgent server for Agent365 integration.

This server handles Activity Protocol messages from Azure Bot Service,
processes them using the Azure AI Foundry agent, and returns responses.
"""

import asyncio
import logging
import sys
from aiohttp import web
import aiohttp_cors

from config import Config
from activity_handler import ActivityHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Global activity handler
activity_handler: ActivityHandler = None


async def init_app():
    """Initialize the application."""
    global activity_handler
    
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        logger.info(f"Config: {Config.to_dict()}")
        
        # Initialize activity handler
        activity_handler = ActivityHandler()
        await activity_handler.initialize()
        logger.info("Activity handler initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


async def handle_messages(request: web.Request) -> web.Response:
    """
    Handle incoming Activity Protocol messages from Bot Service.
    
    POST /api/messages
    """
    try:
        activity = await request.json()
        logger.info(f"Received activity: {activity.get('type')}")
        
        # Process activity
        response_activity = await activity_handler.handle_activity(activity)
        
        return web.json_response(response_activity, status=200)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        return web.json_response(
            {"error": str(e)},
            status=500
        )


async def health_check(request: web.Request) -> web.Response:
    """
    Health check endpoint.
    
    GET /health
    """
    health_status = {
        "status": "healthy",
        "agent": Config.AGENT_NAME,
        "version": Config.AGENT_VERSION,
        "config": Config.to_dict()
    }
    return web.json_response(health_status, status=200)


async def root_handler(request: web.Request) -> web.Response:
    """
    Root endpoint with agent information.
    
    GET /
    """
    info = {
        "name": Config.AGENT_NAME,
        "version": Config.AGENT_VERSION,
        "description": Config.AGENT_DESCRIPTION,
        "type": "hosted_agent",
        "endpoints": {
            "messages": "/api/messages",
            "health": "/health"
        },
        "status": "running"
    }
    return web.json_response(info, status=200)


async def on_startup(app: web.Application):
    """Run on application startup."""
    logger.info("Starting hosted agent server...")
    await init_app()
    logger.info(f"Server started on {Config.HOST}:{Config.PORT}")


async def on_cleanup(app: web.Application):
    """Run on application cleanup."""
    logger.info("Shutting down hosted agent server...")
    if activity_handler:
        await activity_handler.cleanup()
    logger.info("Server shutdown complete")


def create_app() -> web.Application:
    """Create and configure the web application."""
    app = web.Application()
    
    # Configure CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_get("/", root_handler)
    app.router.add_get("/health", health_check)
    app.router.add_post("/api/messages", handle_messages)
    
    # Configure CORS on all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    # Startup/cleanup handlers
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    
    return app


def main():
    """Main entry point."""
    try:
        logger.info(f"Starting {Config.AGENT_NAME} v{Config.AGENT_VERSION}")
        logger.info(f"Server configuration: {Config.to_dict()}")
        
        app = create_app()
        
        web.run_app(
            app,
            host=Config.HOST,
            port=Config.PORT,
            access_log=logger
        )
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
