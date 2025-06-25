import contextlib
import logging
import os
import sys
from collections.abc import AsyncIterator
from fastapi import FastAPI, Request # Request might be used by FastAPI internally or other parts
from app.config.config import settings as app_settings_instance
from app.tools.weather import get_weather
from app.tools.web_search import search_brave, search_google
from mcp.server.fastmcp import FastMCP
from typing import List, Optional

# Logging is now configured in app.config.config
logger = logging.getLogger(__name__)

mcp_server = FastMCP(
    name="Benraz-MCP-Server",
    description="An MCP server using FastMCP"
)

@mcp_server.tool()
async def weather(location: str) -> str:
    """Get the current weather for a location.
    
    Args:
        location: The city and state, e.g., San Francisco, CA
    """
    logger.info(f"Executing weather tool for location: {location}")
    result = await get_weather(location)
    logger.debug(f"Weather tool result: {result}")
    return str(result)

if app_settings_instance.BRAVE_API_KEY:
    @mcp_server.tool()
    async def brave_search_tool(query: str, count: int = 10, sites: Optional[List[str]] = None) -> str:
        """Search the web with Brave Search. Optionally restrict to a list of websites.
        
        Args:
            query: The search query.
            count: Number of search results to return (default: 10, max: 20).
            sites (optional): List of website domains/URLs to restrict the search to. If not provided, search is not restricted.
        Example:
            brave_search_tool(query="AI news", sites=["wired.com", "arstechnica.com"])
        """
        logger.info(f"Executing Brave search tool for query: {query}, count: {count}, sites: {sites}")
        result = await search_brave(query, count, sites)
        logger.debug(f"Brave search result: {result}")
        return str(result)

if app_settings_instance.GOOGLE_API_KEY and app_settings_instance.GOOGLE_CSE_ID:
    @mcp_server.tool()
    async def google_search_tool(query: str, count: int = 10, sites: Optional[List[str]] = None) -> str:
        """Search the web with Google Search. Optionally restrict to a list of websites.
        
        Args:
            query: The search query.
            count: Number of search results to return (default: 10, max: 10).
            sites (optional): List of website domains/URLs to restrict the search to. If not provided, search is not restricted.
        Example:
            google_search_tool(query="AI news", sites=["wired.com", "arstechnica.com"])
        """
        logger.info(f"Executing Google search tool for query: {query}, count: {count}, sites: {sites}")
        result = await search_google(query, count, sites)
        logger.debug(f"Google search result: {result}")
        return str(result)

# FastAPI lifespan to manage FastMCP session manager
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage FastMCP session manager lifecycle"""
    async with mcp_server.session_manager.run():
        logger.info("FastMCP session manager started")
        
        # Log application startup and routes here
        logger.info("FastAPI application startup complete.")
        logger.info(f"MCP Transport Mode from settings: {app_settings_instance.MCP_TRANSPORT_MODE}")
        if app_settings_instance.MCP_TRANSPORT_MODE != "stdio":
            logger.info(f"MCP Server (HTTP/SSE) available at /mcp endpoint on host {app_settings_instance.MCP_SERVER_HOST}:{app_settings_instance.MCP_SERVER_PORT}")

        # Log all registered routes
        logger.info("Registered routes:")
        from starlette.routing import Mount 
        for route_entry in app.routes:
            if hasattr(route_entry, "path") and not isinstance(route_entry, Mount):
                methods_str = str(list(route_entry.methods)) if hasattr(route_entry, 'methods') and route_entry.methods is not None else 'N/A'
                logger.info(f"  Route: Path='{route_entry.path}', Name='{route_entry.name if hasattr(route_entry, 'name') else 'N/A'}', Methods={methods_str}")
            elif isinstance(route_entry, Mount):
                logger.info(f"  Mount: Path='{route_entry.path}', AppName='{route_entry.name if hasattr(route_entry, 'name') else 'N/A'}'")
        
        logger.info("Loaded settings with non-empty values:")
        for k, v in app_settings_instance.env_vars.items():
            if v:
                logger.info(f"  {k} = {v}")
        
        yield
    logger.info("FastMCP session manager stopped")

# Use FastMCP's streamable HTTP app as the primary application
app = mcp_server.streamable_http_app()

# FastMCP apps are Starlette apps, so we need to add routes differently
from starlette.routing import Route
from starlette.responses import JSONResponse

async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "server": "MCP Server with FastMCP", "version": "1.0.0"})

async def ping(request):
    """Basic ping endpoint"""
    return JSONResponse({"message": "pong"})

async def server_info(request):
    """Server information endpoint"""
    return JSONResponse({
        "name": "Benraz-MCP-Server",
        "description": "An MCP server using FastMCP",
        "transport_mode": app_settings_instance.MCP_TRANSPORT_MODE,
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "ping": "/ping"
        },
        "tools": ["weather", "brave_search_tool", "google_search_tool"]
    })

# Add our custom routes to the FastMCP app
app.routes.extend([
    Route("/health", health_check, methods=["GET", "HEAD"]),
    Route("/ping", ping, methods=["GET", "HEAD"]),
    Route("/info", server_info, methods=["GET"])
])

if __name__ == "__main__":
    # This block is primarily for stdio mode or direct execution.
    # Uvicorn for HTTP/SSE mode is typically launched via run.py.
    
    # Ensure logging is configured if running this file directly
    # (config.py should have already done this if imported, but as a safeguard)
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(stream=sys.stdout, 
                            level=app_settings_instance.LOG_LEVEL.upper(), 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info(f"Executing app/main.py directly (__name__ == '__main__')")
    logger.info(f"MCP_TRANSPORT_MODE from settings: {app_settings_instance.MCP_TRANSPORT_MODE}")

    if app_settings_instance.MCP_TRANSPORT_MODE == "stdio":
        logger.info("Starting MCP server in stdio mode via FastMCP.")
        # For stdio mode, FastMCP takes over the stdin/stdout.
        # No FastAPI app or Uvicorn server is run in this case.
        mcp_server.run(transport="stdio") # This is a blocking call
        logger.info("MCP server (stdio mode) finished.")
    else:
        logger.info("Running app/main.py directly in non-stdio mode.")
        logger.info("This typically means Uvicorn should be used (e.g., via run.py) to serve the FastAPI app.")
        logger.info(f"To run in HTTP/SSE mode, execute: uvicorn app.main:app --host {app_settings_instance.MCP_SERVER_HOST} --port {app_settings_instance.MCP_SERVER_PORT} --reload")
        # If you want to run uvicorn directly from here for http mode when __name__ == "__main__":
        # import uvicorn
        # uvicorn.run(app, host=app_settings_instance.MCP_SERVER_HOST, port=app_settings_instance.MCP_SERVER_PORT)
        print(f"Server configured for {app_settings_instance.MCP_TRANSPORT_MODE} mode. Please use run.py or Uvicorn directly to start.", file=sys.stderr)
