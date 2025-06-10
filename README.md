# Python MCP Server 🚀

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

A fully functional **Model Context Protocol (MCP) server** built with Python and FastAPI, featuring real-time weather data, web search capabilities, and a robust HTTP/SSE transport layer. This server demonstrates best practices for MCP implementation with proper async handling, configuration management, and extensible tool architecture.

## ✨ **What's Working Right Now**

- ✅ **Fully Operational MCP Server** - Running on HTTP transport with auto-reload
- ✅ **Real-time Weather Tool** - Live weather data using wttr.in API
- ✅ **Web Search Tools** - Brave Search and Google Search implementations
- ✅ **Complete MCP Protocol Support** - Tool discovery, calling, resources, and prompts
- ✅ **Health Monitoring** - `/health` and `/info` endpoints for monitoring
- ✅ **Professional Logging** - Comprehensive structured logging
- ✅ **Async Session Management** - Proper FastMCP lifecycle management
- ✅ **Test Client Included** - Ready-to-use MCP client for testing

## 🌟 **Key Features**

### **Core MCP Implementation**
- **Standards Compliant**: Full adherence to Model Context Protocol specifications
- **HTTP/SSE Transport**: Persistent connections with Server-Sent Events
- **Tool Discovery**: Dynamic tool registration and discovery
- **Resource Management**: Complete resource and prompt handling
- **Session Lifecycle**: Proper async session management with FastMCP

### **Built-in Tools**
- **🌤️ Weather Tool**: Real-time weather data from wttr.in (no API key required)
- **🔍 Brave Search**: Web search via Brave Search API (API key required)
- **🔎 Google Search**: Web search via Google Custom Search (API key required)
- **📊 System Info**: Server health and information endpoints

### **Production Ready**
- **Auto-reload Development**: Hot reloading during development
- **Structured Logging**: Comprehensive logging with proper levels
- **Error Handling**: Robust async error handling across all tools
- **Configuration Management**: Environment-based configuration
- **Docker Support**: Complete containerization with Docker Compose
- **Health Monitoring**: Built-in health check and server info endpoints

## 📁 **Project Structure**

```
py-mcp-server/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI app with FastMCP integration
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── config.py              # Settings and logging configuration
│   ├── core/                      # Core MCP logic
│   │   ├── __init__.py
│   │   └── mcp_core.py            # MCP base classes and utilities
│   ├── tools/                     # Tool implementations
│   │   ├── __init__.py
│   │   ├── weather.py             # Weather tool (wttr.in API)
│   │   └── web_search.py          # Brave/Google search tools
│   └── transports/                # Transport layer (future expansion)
│       └── __init__.py
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore patterns
├── docker-compose.yml             # Docker Compose configuration
├── Dockerfile                     # Docker build configuration
├── requirements.txt               # Python dependencies
├── run.py                         # Server startup script
├── test_mcp_client.py            # MCP client for testing
└── README.md                      # This documentation
```

## 🚀 **Quick Start**

### **Prerequisites**
- **Python 3.11+** (recommended 3.11 or higher)
- **pip** package manager
- **Git** for version control
- **Docker & Docker Compose** (optional, for containerized deployment)

### **Optional API Keys** (for enhanced functionality)
- **Brave Search API Key** - For web search capabilities
- **Google Custom Search API Key + CX ID** - For Google search integration

### **1. Clone and Setup**
```bash
# Clone the repository
git clone <your-repo-url>
cd py-mcp-server

# Create virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# For Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Configure Environment (Optional)**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your API keys (optional)
# BRAVE_API_KEY=your_brave_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here
# GOOGLE_CX=your_google_custom_search_engine_id
```

### **4. Start the Server**
```bash
python run.py
```

🎉 **That's it!** Your MCP server is now running at `http://localhost:8001`

### **5. Test the Server**
```bash
# Test weather tool (works without API keys)
python test_mcp_client.py

# Check server health
curl http://localhost:8001/health

# View server info
curl http://localhost:8001/info
```

## 🛠️ **Available Tools**

### **🌤️ Weather Tool** *(Fully Functional)*
Get comprehensive weather information for any location using the wttr.in API.

**Usage:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "weather",
    "arguments": {
      "location": "San Francisco, CA"
    }
  }
}
```

**Features:**
- ✅ **No API Key Required** - Uses free wttr.in service
- ✅ **Detailed Forecasts** - Current conditions, 3-day forecast, hourly data
- ✅ **Global Coverage** - Works for cities worldwide
- ✅ **Multiple Formats** - Temperature, humidity, wind, precipitation

### **🔍 Web Search Tools** *(API Keys Required)*

#### **Brave Search**
```json
{
  "method": "tools/call",
  "params": {
    "name": "brave_search_tool",
    "arguments": {
      "query": "python fastapi tutorial"
    }
  }
}
```

#### **Google Search** 
```json
{
  "method": "tools/call",
  "params": {
    "name": "google_search_tool",
    "arguments": {
      "query": "machine learning python"
    }
  }
}
```

**Note:** Search tools require valid API keys in your `.env` file to function properly.

## 🔧 **Server Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST/SSE | Main MCP protocol endpoint |
| `/health` | GET | Server health check |
| `/info` | GET | Server information and capabilities |
| `/docs` | GET | Interactive API documentation |
| `/` | GET | Welcome message |

## 🐳 **Docker Deployment**

### **🚀 Optimized Docker Configuration**

This project includes **two optimized Docker configurations**:

| Configuration | Image Size | Use Case | Build Time |
|---------------|------------|----------|------------|
| **Standard** (`Dockerfile`) | 181MB | General development | ~45s |
| **Alpine** (`Dockerfile.alpine`) | 111MB | **Production (Recommended)** | ~40s |

**📦 Size Comparison**: Alpine version is **38.7% smaller** (70MB reduction)

### **🎯 Production Deployment (Recommended)**
```bash
# Using optimized Alpine image with Docker Compose
docker-compose up --build

# Run in background (detached mode)
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### **🛠️ Development Mode**
```bash
# Start development container with hot reloading
docker-compose --profile development up --build

# This runs on port 8001 with source code mounting
```

### **📊 Multi-Stage Builds**
Both Dockerfiles use **multi-stage builds** for optimization:
- **Builder stage**: Compiles dependencies in virtual environment
- **Production stage**: Minimal runtime image with only necessary components
- **Development stage**: Additional tools for debugging (Alpine only)

### **🔐 Security Features**
- ✅ **Non-root user** (mcpuser:1001) for security
- ✅ **Minimal attack surface** with Alpine Linux
- ✅ **Health checks** built into containers
- ✅ **Resource limits** configured in docker-compose.yml

### **Using Docker Directly**
```bash
# Build Alpine image (recommended for production)
docker build -f Dockerfile.alpine -t py-mcp-server:alpine .

# Build standard image
docker build -t py-mcp-server:standard .

# Run Alpine container
docker run -p 8001:8001 --env-file .env py-mcp-server:alpine

# Run with resource limits
docker run -p 8001:8001 --env-file .env \
  --memory=512m --cpus=1.0 \
  py-mcp-server:alpine
```

### **🔧 Docker Configuration Options**

#### **Environment Variables for Docker**
```bash
# Port configuration (original port 8001)
MCP_SERVER_PORT=8001

# Environment mode
ENV=production

# Resource optimization
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

#### **Volume Mounts**
```bash
# Persistent logs
./logs:/app/logs:rw

# Development source mounting
.:/app:rw  # Development only
```

### **🏗️ Build Targets**
```bash
# Production build (default)
docker build -f Dockerfile.alpine --target production -t mcp:prod .

# Development build with additional tools
docker build -f Dockerfile.alpine --target development -t mcp:dev .
```

## 🧪 **Testing the Server**

### **Using the Included Test Client**
```bash
# Test weather tool (works without API keys)
python test_mcp_client.py

# Expected output:
# Connected to MCP server successfully!
# Available tools: ['weather', 'brave_search_tool', 'google_search_tool']
# Weather result: [Detailed weather information for San Francisco]
```

### **Manual Testing with curl**
```bash
# Test server health
curl http://localhost:8001/health

# Get server information
curl http://localhost:8001/info

# Test MCP tool discovery
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

### **Expected Server Logs**
```
2025-06-09 19:24:01,509 - mcp.server.streamable_http_manager - INFO - StreamableHTTP session manager started
2025-06-09 19:24:01,510 - app.main - INFO - FastMCP session manager started
2025-06-09 19:24:01,511 - app.main - INFO - MCP Server (HTTP/SSE) available at /mcp endpoint on host 0.0.0.0:8001
2025-06-09 19:24:01,512 - app.main - INFO - Registered routes:
2025-06-09 19:24:01,512 - app.main - INFO -   Route: Path='/health', Name='health_check', Methods=['GET']
2025-06-09 19:24:01,512 - app.main - INFO -   Route: Path='/info', Name='server_info', Methods=['GET']
```

## ⚙️ **Configuration**

### **Environment Variables**
Create a `.env` file in the project root with the following options:

```env
# API Keys (Optional - Weather tool works without any keys)
BRAVE_API_KEY=your_brave_search_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_google_custom_search_engine_id

# Server Configuration
MCP_TRANSPORT_MODE=http          # Transport mode: 'http' or 'stdio'
MCP_SERVER_HOST=0.0.0.0         # Server host address
MCP_SERVER_PORT=8001            # Server port number
LOG_LEVEL=INFO                  # Logging level: DEBUG, INFO, WARNING, ERROR
```

### **Configuration Files**
- **`app/config/config.py`** - Main configuration management
- **`.env`** - Environment-specific variables
- **`requirements.txt`** - Python dependencies
- **`docker-compose.yml`** - Docker deployment configuration

## 🔧 **Development**

### **Adding New Tools**
1. **Create a new tool file** in `app/tools/`:
```python
# app/tools/my_new_tool.py
import asyncio
from typing import Any

async def my_new_tool(param1: str, param2: int = 10) -> dict[str, Any]:
    """Description of what your tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (optional)
    
    Returns:
        Dictionary with tool results
    """
    # Your tool implementation here
    result = {"message": f"Processing {param1} with value {param2}"}
    return result
```

2. **Register in main.py**:
```python
# In app/main.py
from app.tools.my_new_tool import my_new_tool

@mcp_server.tool()
async def my_new_tool_endpoint(param1: str, param2: int = 10) -> str:
    """Tool description for MCP clients"""
    result = await my_new_tool(param1, param2)
    return str(result)
```

### **Project Architecture**
- **`app/main.py`** - FastAPI application and MCP server setup
- **`app/config/`** - Configuration and logging management  
- **`app/tools/`** - Individual tool implementations
- **`app/core/`** - Core MCP utilities and base classes
- **`app/transports/`** - Transport layer implementations (future)

### **Development Commands**
```bash
# Start development server with auto-reload
python run.py

# Run with debug logging
LOG_LEVEL=DEBUG python run.py

# Test specific tool
python -c "from app.tools.weather import get_weather; import asyncio; print(asyncio.run(get_weather('London')))"
```

## 📊 **Monitoring & Health Checks**

### **Health Check Endpoint**
```bash
curl http://localhost:8001/health
```
**Response:**
```json
{
  "status": "healthy",
  "server": "MCP Server with FastMCP",
  "version": "1.0.0"
}
```

### **Server Information Endpoint**
```bash
curl http://localhost:8001/info  
```
**Response:**
```json
{
  "name": "Benraz-MCP-Server",
  "description": "An MCP server using FastMCP",
  "transport_mode": "http",
  "endpoints": {
    "mcp": "/mcp",
    "health": "/health", 
    "info": "/info"
  },
  "tools": ["weather", "brave_search_tool", "google_search_tool"]
}
```

### **Logging**
The server provides comprehensive structured logging:
- **INFO level**: General operation information
- **DEBUG level**: Detailed execution traces  
- **ERROR level**: Error conditions and exceptions
- **Tool execution**: Detailed tool call logging

## 🚦 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Error: [Errno 10048] Only one usage of each socket address
# Solution: Change port in .env file
MCP_SERVER_PORT=8002
```

#### **Import Errors**
```bash
# Error: ModuleNotFoundError
# Solution: Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate     # Linux/macOS
```

#### **API Key Issues**
```bash
# Brave Search returns 422 error
# Solution: Add valid API key to .env file
BRAVE_API_KEY=your_actual_api_key_here
```

### **Checking Server Status**
```bash
# Check if server is running  
curl -f http://localhost:8001/health || echo "Server not responding"

# View detailed server logs
tail -f server.log  # If logging to file

# Test MCP protocol
python test_mcp_client.py
```

## 📚 **API Documentation**

### **Interactive Documentation**
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc  
- **OpenAPI Spec**: http://localhost:8001/openapi.json

### **MCP Protocol Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mcp` | Main MCP protocol communication |
| GET | `/health` | Server health status |
| GET | `/info` | Server capabilities and information |

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-tool`
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Submit a pull request

### **Code Style**
- Follow PEP 8 Python style guide
- Use type hints for all function parameters and returns
- Add comprehensive docstrings to all functions
- Include proper error handling and logging

### **Testing**
```bash
# Run the test client
python test_mcp_client.py

# Test individual tools
python -m app.tools.weather
python -m app.tools.web_search
```

## 📄 **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🔗 **Resources**
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Docker Documentation](https://docs.docker.com)

---

**🎉 Ready to extend your MCP server?** The architecture is designed for easy expansion - add new tools, integrate APIs, and build powerful AI-assisted workflows!
