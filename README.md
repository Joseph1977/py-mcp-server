# Python MCP Server

This project implements a Model Context Protocol (MCP) server in Python using FastAPI. It supports both HTTP/SSE and stdio transports and can be containerized using Docker.

The server provides a modular architecture for integrating and exposing various tools, such as web search (Brave, Google) and weather information. Configuration is managed via environment variables.

## Features

*   **MCP Implementation**: Adheres to the Model Context Protocol.
*   **Dual Transport Modes**:
    *   HTTP/SSE: For persistent services, accessible via HTTP POST requests with Server-Sent Events for responses.
    *   Stdio: For direct command-line interaction, reading JSON requests from stdin and writing JSON responses to stdout.
*   **Tool Integration**:
    *   Web Search: Brave Search, Google Search (requires API keys and configuration).
    *   Weather Information: OpenWeatherMap (requires API key).
    *   Easily extensible for more tools.
*   **Configuration**: Uses environment variables (via `.env` file) for API keys and server settings.
*   **Dockerized**: Includes `Dockerfile` and `docker-compose.yml` for easy containerization and deployment.
*   **Modular Architecture**: Code is organized into modules for configuration, core MCP logic, tools, and transports.

## Project Structure

```
py-mcp-server/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py             # FastAPI app, transport handlers, startup logic
│   ├── config/             # Configuration loading
│   │   ├── __init__.py
│   │   └── config.py       # Loads .env variables
│   ├── core/               # Core MCP logic (placeholders for SDK)
│   │   ├── __init__.py
│   │   └── mcp_core.py     # MCPModel, MCPTool placeholders
│   ├── tools/              # Tool implementations
│   │   ├── __init__.py
│   │   ├── weather.py
│   │   └── web_search.py
│   └── transports/         # (Currently integrated in main.py, can be separated)
│       └── __init__.py
├── .env.example            # Example environment file (copy to .env)
├── .gitignore
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker build instructions
├── requirements.txt        # Python dependencies
├── run.py                  # Script to run the Uvicorn server
└── README.md               # This file
```

## Prerequisites

*   Python 3.10+
*   Docker and Docker Compose (for containerized deployment)
*   API Keys for services you want to use:
    *   Brave Search API Key
    *   Google Search API Key & Custom Search Engine ID (CX)
    *   OpenWeatherMap API Key

## Setup and Configuration

1.  **Clone the repository (if you haven\'t already):**
    ```bash
    # git clone <repository-url>
    # cd py-mcp-server
    ```

2.  **Create and configure the environment file:**
    Copy `.env.example` (or the `.env` file previously created) to `.env` in the project root:
    ```bash
    cp .env.example .env
    ```
    Open `.env` and fill in your API keys and desired settings:
    ```env
    BRAVE_API_KEY="your_brave_api_key"
    GOOGLE_API_KEY="your_google_api_key"
    # You\'ll also need your Google Custom Search Engine ID (CX) for the google_search tool
    OPENWEATHERMAP_API_KEY="your_openweathermap_api_key"

    LOG_LEVEL="INFO"
    MCP_TRANSPORT_MODE="sse" # "sse" or "stdio"
    ```

## Running Locally (Without Docker)

1.  **Create and activate a Python virtual environment:**
    (In PowerShell, from the project root `c:\\GitRepo\\ML-AI\\MCP\\py-mcp-server`)
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
    For other shells (bash/zsh):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Transport Mode (Optional, defaults to "sse" if not in `.env`):**
    To use stdio transport for the local run:
    (PowerShell)
    ```powershell
    $env:MCP_TRANSPORT_MODE="stdio"
    ```
    (bash/zsh)
    ```bash
    export MCP_TRANSPORT_MODE="stdio"
    ```
    If `MCP_TRANSPORT_MODE` is set to `sse` or not set, the server will start in SSE mode.

4.  **Run the application:**
    ```bash
    python run.py
    ```
    The server will start, typically on `http://0.0.0.0:8000` for SSE mode.
    You will see log messages indicating the transport mode in use.

## Running with Docker

1.  **Ensure Docker Desktop is running.**
2.  **Build and run the container using Docker Compose:**
    From the project root directory (`c:\\GitRepo\\ML-AI\\MCP\\py-mcp-server`):
    ```bash
    docker-compose up --build
    ```
    This will build the Docker image (if it doesn\'t exist or has changed) and start the service. The server will be accessible on `http://localhost:8000` if `MCP_TRANSPORT_MODE` in your `.env` file is set to `sse` (or is unset).
    To run in the background (detached mode):
    ```bash
    docker-compose up --build -d
    ```

3.  **To stop the Docker Compose services:**
    ```bash
    docker-compose down
    ```

## Using the MCP Server

The server expects JSON requests and (for SSE) streams JSON responses.

### SSE Transport (`MCP_TRANSPORT_MODE="sse"`)

*   **Endpoint**: `POST http://localhost:8000/mcp/sse`
*   **Request Body**: JSON object specifying the tool and its parameters.
    ```json
    {
        "tool_name": "tool_to_execute",
        "params": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    ```
*   **Example with `curl`:**
    ```bash
    curl -X POST -H "Content-Type: application/json" \
         -d \'{"tool_name": "get_weather", "params": {"location": "London"}}\' \
         http://localhost:8000/mcp/sse
    ```
    This will stream Server-Sent Events. Each event will have a `data` field containing a JSON string.

### Stdio Transport (`MCP_TRANSPORT_MODE="stdio"`)

*   When the server is run with `MCP_TRANSPORT_MODE="stdio"`, it will print:
    ```
    Starting MCP server with stdio transport.
    MCP Server Ready (stdio)
    ```
*   **Input**: Type or pipe a JSON request (as shown above) directly into the terminal where the server is running, followed by a newline.
*   **Output**: The server will print a JSON response to stdout.
*   **Example Interaction:**
    ```
    # (Server is running in stdio mode)
    # Type this and press Enter:
    {"tool_name": "get_weather", "params": {"location": "Berlin"}}

    # Server responds (example):
    {"coord":{"lon":13.4105,"lat":52.5244},"weather":...,"main":{...},...}
    ```

## Available Tools (Placeholders)

*   **`brave_search`**: Searches the web using Brave Search.
    *   Params: `{"query": "your search query"}`
*   **`google_search`**: Searches the web using Google Search.
    *   Params: `{"query": "your search query"}`
    *   Note: Requires `GOOGLE_API_KEY` and a configured Custom Search Engine ID (CX) in `app/tools/web_search.py`.
*   **`get_weather`**: Gets the current weather for a location.
    *   Params: `{"location": "city_name"}`

**Important**: The tool implementations in `app/tools/` currently use placeholder API URLs and may require the actual MCP Python SDK for full functionality. You will need to:
1.  Install the official MCP Python SDK.
2.  Update `app/core/mcp_core.py` to use the real SDK components.
3.  Update the tool functions in `app/tools/` to correctly use the SDK and make actual API calls with proper error handling.

## Development

*   **Adding New Tools**:
    1.  Create a new Python file in the `app/tools/` directory (e.g., `my_new_tool.py`).
    2.  Define your tool function(s) and an `MCPTool` instance (similar to `weather.py` or `web_search.py`).
    3.  Import your tool list in `app/main.py` and add it to the `all_tools` list.
*   **MCP SDK Integration**:
    *   The current `app/core/mcp_core.py` contains simplified placeholders for `MCPModel` and `MCPTool`.
    *   Once the official MCP Python SDK is available, replace these placeholders with the actual SDK classes and adapt the server logic accordingly.

## Stopping the Server

*   **Local Run (Python directly)**: Press `Ctrl+C` in the terminal where `python run.py` is executing.
*   **Docker Compose**:
    *   If running in the foreground: `Ctrl+C` in the terminal.
    *   If running detached (`-d`): `docker-compose down` in the project root.

This README.md provides a comprehensive guide to setting up, running, and developing your Python MCP server.
