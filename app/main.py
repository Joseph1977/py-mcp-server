import logging
import os
import sys
import uuid # Added import for uuid

# Configure logging as early as possible
# Determine log level from environment variable or default to INFO
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level_str, logging.INFO)
# Ensure basicConfig is called only once, preferably at the very start.
# It might be better in run.py if that's the true entry point for all modes.
# For now, let's assume main.py can be an entry point too (e.g. for stdio direct run)
if not logging.getLogger().hasHandlers(): # Check if handlers are already configured
    logging.basicConfig(stream=sys.stdout, level=numeric_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
print(f"app.main.py: Logging configured with level {log_level_str}")

print("START OF app.main.py execution") # New print

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
# Ensure app_settings_instance is imported correctly from app.config.config
# This imports the 'settings' instance created at the end of config.py
from app.config.config import settings as app_settings_instance 
from app.core.mcp_core import MCPModel, MCPTool # MCPTool added
from app.tools.weather import get_weather
from app.tools.web_search import search_brave, search_google
from sse_starlette.sse import EventSourceResponse
import asyncio
import json # For parsing request body

print(f"app.main.py: Imports completed. Checking imported settings instance...")
if hasattr(app_settings_instance, 'MCP_TRANSPORT_MODE'):
    print(f"app.main.py: app_settings_instance.MCP_TRANSPORT_MODE: {app_settings_instance.MCP_TRANSPORT_MODE}")
else:
    print("app.main.py: MCP_TRANSPORT_MODE NOT FOUND on imported app_settings_instance")
    print(f"app.main.py: dir(app_settings_instance): {dir(app_settings_instance)}")
    if hasattr(app_settings_instance, '__dict__'):
        print(f"app.main.py: app_settings_instance.__dict__: {app_settings_instance.__dict__}")


app = FastAPI()
mcp_model: MCPModel = None # Global variable for the MCPModel
# sse_queue is no longer a single global queue; client-specific queues are in sse_client_queues

# Use the imported instance directly. This is crucial.
# The 'settings' variable in app.config.config is an INSTANCE of the Settings class.
settings_object_from_config = app_settings_instance
print(f"app.main.py: 'settings_object_from_config' variable assigned from imported app_settings_instance.")
if hasattr(settings_object_from_config, 'MCP_TRANSPORT_MODE'):
    print(f"app.main.py: settings_object_from_config.MCP_TRANSPORT_MODE: {settings_object_from_config.MCP_TRANSPORT_MODE}")
else:
    print(f"app.main.py: MCP_TRANSPORT_MODE NOT FOUND on settings_object_from_config.")
    print(f"app.main.py: dir(settings_object_from_config): {dir(settings_object_from_config)}")
    if hasattr(settings_object_from_config, '__dict__'):
        print(f"app.main.py: settings_object_from_config.__dict__: {settings_object_from_config.__dict__}")


# Global dictionary to store SSE queues for different clients
sse_client_queues = {}


async def sse_event_publisher(client_id: str):
    """
    Listens to a client-specific queue and yields events for EventSourceResponse.
    A simple global queue is used here for now.
    """
    # Get the queue for this specific client
    # If the client_id is not in sse_client_queues, this means the connection was closed
    # or the queue was not properly initialized. Handle this gracefully.
    if client_id not in sse_client_queues:
        logger.warning(f"SSE event publisher started for unknown client_id: {client_id}. Terminating.")
        return

    local_queue = sse_client_queues[client_id]
    logger.info(f"SSE event publisher started for client_id: {client_id}")
    try:
        while True:
            message_to_send = await local_queue.get()
            if message_to_send is None: # Sentinel value to stop the publisher
                logger.info(f"SSE event publisher for {client_id} received None, stopping.")
                break
            yield {"id": str(uuid.uuid4()), "event": "message", "data": json.dumps(message_to_send)}
            logger.debug(f"SSE event publisher for {client_id} sent message: {message_to_send}")
    except asyncio.CancelledError:
        logger.info(f"SSE event publisher for {client_id} was cancelled.")
    except Exception as e:
        logger.error(f"Error in SSE event publisher for {client_id}: {e}", exc_info=True)
    finally:
        logger.info(f"SSE event publisher for {client_id} finished.")
        # Clean up the client's queue when the publisher stops
        if client_id in sse_client_queues:
            del sse_client_queues[client_id]
            logger.info(f"Cleaned up SSE queue for client_id: {client_id}")


@app.on_event("startup")
async def startup_event():
    global mcp_model # sse_queue is no longer global for individual messages
    print("START app.main.startup_event") # New print
    logger.info("Application startup event triggered.")
    
    tools = [
        MCPTool("get_weather", "Get the current weather for a location", get_weather, {"type": "object", "properties": {"location": {"type": "string", "description": "The city and state, e.g., San Francisco, CA"}}, "required": ["location"]}),
        MCPTool("brave_search", "Search the web with Brave Search", search_brave, {"type": "object", "properties": {"query": {"type": "string", "description": "The search query"}}, "required": ["query"]}),
        MCPTool("google_search", "Search the web with Google Search", search_google, {"type": "object", "properties": {"query": {"type": "string", "description": "The search query"}}, "required": ["query"]})
    ]
    mcp_model = MCPModel(tools=tools)
    # Corrected logging: mcp_model.tools is a dict; log its keys or values' names.
    # Logging tool names (keys of the dictionary)
    logger.info(f"MCPModel initialized with tools: {list(mcp_model.tools.keys())}.")

    # Critical point for debugging settings
    print("--- In app.main.py startup_event (diagnostics for settings_object_from_config) ---")
    print(f"Type of settings_object_from_config: {type(settings_object_from_config)}")
    print(f"dir(settings_object_from_config): {dir(settings_object_from_config)}")
    # Check if __dict__ exists, as it might not for all object types or if slots are used.
    if hasattr(settings_object_from_config, '__dict__'):
        print(f"settings_object_from_config.__dict__: {settings_object_from_config.__dict__}")
    else:
        print("settings_object_from_config has no __dict__ attribute.")
    
    # Accessing MCP_TRANSPORT_MODE from the 'settings_object_from_config' instance
    try:
        # Ensure this is the correct variable name used throughout this scope
        transport_mode = settings_object_from_config.MCP_TRANSPORT_MODE 
        logger.info(f"Transport mode selected from settings_object_from_config: {transport_mode}")
        print(f"Transport mode successfully read from settings_object_from_config: {transport_mode}")
    except AttributeError as e:
        logger.error(f"CRITICAL ERROR in startup_event: Failed to get MCP_TRANSPORT_MODE from settings_object_from_config. Error: {e}")
        print(f"CRITICAL ERROR in startup_event: Failed to get MCP_TRANSPORT_MODE from settings_object_from_config. Error: {e}")
        # Attempt to access from the class directly as a fallback diagnostic
        try:
            from app.config.config import Settings as AppSettings # Local import for diagnostics
            class_transport_mode = AppSettings.MCP_TRANSPORT_MODE
            logger.warning(f"Diagnostic: AppSettings.MCP_TRANSPORT_MODE (class attribute) is: {class_transport_mode}")
            print(f"Diagnostic: AppSettings.MCP_TRANSPORT_MODE (class attribute) is: {class_transport_mode}")
        except Exception as e_class:
            logger.error(f"Diagnostic: Failed to access AppSettings.MCP_TRANSPORT_MODE directly from class. Error: {e_class}")
            print(f"Diagnostic: Failed to access AppSettings.MCP_TRANSPORT_MODE directly from class. Error: {e_class}")
        raise # Re-raise the original AttributeError to halt on error

    if transport_mode == "stdio":
        logger.info("Stdio transport mode selected. Starting stdio main loop.")
        print("Stdio transport mode selected. Starting stdio main loop.")
        asyncio.create_task(stdio_main_loop())
    elif transport_mode == "sse":
        logger.info("SSE transport mode selected. SSE endpoints will be active.")
        print("SSE transport mode selected. SSE endpoints will be active.")
    else:
        logger.error(f"Invalid MCP_TRANSPORT_MODE: {transport_mode}. Defaulting to SSE.")
        print(f"Invalid MCP_TRANSPORT_MODE: {transport_mode}. Defaulting to SSE.")
        # Optionally, set a default or raise an error
    print("END app.main.startup_event")


@app.get("/mcp/sse", summary="Establish SSE connection for MCP events")
async def sse_stream_endpoint(request: Request):
    """
    Handles GET requests to establish the Server-Sent Events stream.
    """
    # A simple client identifier, could be enhanced (e.g., from headers, tokens)
    client_ip = request.client.host if request.client else "unknown_client"
    client_id = f"{client_ip}_{uuid.uuid4()}" # Simple unique ID for the connection
    
    # Create a new queue for this client
    sse_client_queues[client_id] = asyncio.Queue()
    logger.info(f"SSE connection opened for client_id: {client_id} from {client_ip}. Queue created.")
    
    # Return an EventSourceResponse that uses the client-specific publisher
    return EventSourceResponse(sse_event_publisher(client_id), media_type="text/event-stream")


@app.post("/mcp/sse", summary="Receive MCP message from client via POST")
async def mcp_message_receiver_post(request: Request):
    """
    Handles POST requests from the client, processes them.
    For 'initialize', responds directly.
    For other methods, queues the response to be sent over the SSE stream.
    """
    client_ip = request.client.host if request.client else "unknown_client"
    # Try to find a client_id. This is tricky with POST as it's a separate request.
    # For a robust solution, client_id might need to be passed in headers or body.
    # For now, we'll log a warning if we can't find a queue. This part needs refinement.
    # This simplistic approach will broadcast to all connected clients if not scoped.
    # A better approach would be to identify the specific client from the request.
    # For now, let's assume the client includes a 'client_id' in the request body for routing.

    raw_body = await request.body()
    client_ip = request.client.host if request.client else "unknown_client"
    logger.info(f"MCP Message Receiver (POST): Received request from {client_ip}")
    logger.debug(f"MCP Message Receiver (POST): Raw body: {raw_body.decode()}")

    try:
        request_data_dict = json.loads(raw_body.decode())
    except json.JSONDecodeError as e:
        logger.error(f"MCP Message Receiver (POST): JSON decode error: {e}")
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format", "detail": str(e)})

    logger.info(f"MCP Message Receiver (POST): Parsed JSON request: {request_data_dict}")

    response_from_core = await mcp_model.process_request(request_data_dict)
    
    logger.info(f"MCP Message Receiver (POST): Core processed request, response: {response_from_core}")

    if request_data_dict.get("method") == "initialize":
        logger.info("MCP Message Receiver (POST): Method is 'initialize', sending direct synchronous response.")
        return JSONResponse(content=response_from_core)
    else:
        # If client_id is provided and valid, send to specific client queue
        client_id_from_request = request_data_dict.get("client_id")
        if client_id_from_request and client_id_from_request in sse_client_queues:
            await sse_client_queues[client_id_from_request].put(response_from_core)
            logger.info(f"Response for {client_id_from_request} queued for SSE stream.")
            return JSONResponse({"status": "queued", "client_id": client_id_from_request})
        else:
            # Fallback or error if client_id is missing/invalid for non-initialize requests
            logger.warning(f"MCP SSE POST: No valid client_id provided for non-initialize request from {client_ip}. Cannot route SSE message. Request data: {request_data_dict}")
            # It's problematic to send an SSE message here without a specific client queue.
            # For now, return an error or a generic success if the action was performed but not streamed.
            # This indicates a design consideration for client identification in POST requests.
            return JSONResponse({"status": "processed_but_not_streamed_no_valid_client_id"}, status_code=202) 


async def stdio_main_loop():
    logger.info("Starting stdio main loop...")
    while True:
        try:
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                logger.info("EOF received, exiting stdio loop.")
                break
            try:
                request_data = json.loads(line.strip())
                logger.info(f"Stdio request: {request_data}")
                if not mcp_model:
                    logger.error("MCP model not initialized for stdio request.")
                    response_str = json.dumps({"error": "MCP model not initialized"})
                else:
                    response_data = await mcp_model.process_request(request_data)
                    response_str = json.dumps(response_data)
                
                print(response_str, flush=True)
                logger.info(f"Stdio response: {response_str}")
            except json.JSONDecodeError:
                logger.error(f"Stdio: Invalid JSON received: {line.strip()}")
                print(json.dumps({"error": "Invalid JSON"}), flush=True)
            except Exception as e:
                logger.error(f"Error processing stdio request: {e}", exc_info=True)
                print(json.dumps({"error": str(e)}), flush=True)
        except Exception as e:
            logger.error(f"Critical error in stdio_main_loop: {e}", exc_info=True)
            await asyncio.sleep(1)


# Note: To run stdio_main_loop when MCP_TRANSPORT_MODE is 'stdio',
# you would typically not use Uvicorn directly in run.py, or Uvicorn would not serve HTTP.
# The run.py script would just call asyncio.run(stdio_main_loop()).
# For now, the startup event logs the mode, but this main.py is primarily set up for Uvicorn/FastAPI (SSE).
# If you want to run stdio, you'd typically execute: python -m app.main (if __main__ guard added) or similar.

# For Uvicorn to pick this up if run directly (e.g. uvicorn app.main:app)
# This is usually handled by run.py
if __name__ == "__main__":
    # This block is for direct execution (e.g., python app/main.py)
    # It's not typically used when run.py and Uvicorn are managing the process.
    # However, it can be useful for deciding whether to run HTTP server or stdio loop.
    
    # Re-check settings here if running main.py directly
    if not hasattr(settings_object_from_config, 'MCP_TRANSPORT_MODE'):
        print("CRITICAL: MCP_TRANSPORT_MODE not found on settings_object_from_config in __main__ block.")
        logger.critical("CRITICAL: MCP_TRANSPORT_MODE not found on settings_object_from_config in __main__ block.")
        sys.exit(1)
    print(f"__main__ block: settings_object_from_config.MCP_TRANSPORT_MODE = {settings_object_from_config.MCP_TRANSPORT_MODE}")
    logger.info(f"__main__ block: settings_object_from_config.MCP_TRANSPORT_MODE = {settings_object_from_config.MCP_TRANSPORT_MODE}")
    if settings_object_from_config.MCP_TRANSPORT_MODE == "stdio":
        print("Transport mode is stdio, running stdio_main_loop.")
        logger.info("Transport mode is stdio, running stdio_main_loop.")
        if not mcp_model: 
            print("Initializing MCPModel for stdio direct run...")
            logger.info("Initializing MCPModel for stdio direct run...")
            tools = [
                MCPTool("get_weather", "Get the current weather for a location", get_weather, {"type": "object", "properties": {"location": {"type": "string", "description": "The city and state, e.g., San Francisco, CA"}}, "required": ["location"]}),
                MCPTool("brave_search", "Search the web with Brave Search", search_brave, {"type": "object", "properties": {"query": {"type": "string", "description": "The search query"}}, "required": ["query"]}),
                MCPTool("google_search", "Search the web with Google Search", search_google, {"type": "object", "properties": {"query": {"type": "string", "description": "The search query"}}, "required": ["query"]})
            ]
            mcp_model = MCPModel(tools=tools)
            logger.info(f"MCPModel initialized with tools: {list(mcp_model.tools.keys())}.")
        else:
            print("MCPModel already initialized.")
            logger.info("MCPModel already initialized.")
        asyncio.run(stdio_main_loop())
    else:
        print(f"Transport mode is '{settings_object_from_config.MCP_TRANSPORT_MODE}'. This script should be run with Uvicorn for SSE/HTTP modes as in run.py.")
        logger.warning(f"main.py run directly with transport mode '{settings_object_from_config.MCP_TRANSPORT_MODE}'. Uvicorn is recommended.")

print("END OF app.main.py execution")
