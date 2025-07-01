# Technical Specification

## System Requirements
- **Python**: 3.11+ (recommended 3.11.x)
- **Memory**: 256MB minimum, 512MB recommended
- **CPU**: 0.5 cores minimum, 1.0 core recommended
- **Network**: HTTP/HTTPS outbound for API calls
- **Storage**: 100MB for application + logs

## Dependencies
```
fastapi>=0.104.0     # Web framework
uvicorn>=0.24.0      # ASGI server
mcp[cli]>=1.0.0      # MCP protocol implementation
httpx>=0.25.0        # Async HTTP client
python-dotenv>=1.0.0 # Environment management
```

## Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MCP_SERVER_PORT` | No | 8001 | Server port |
| `MCP_TRANSPORT_MODE` | No | http | Transport mode |
| `LOG_LEVEL` | No | INFO | Logging level |
| `BRAVE_API_KEY` | No | - | Brave Search API key |
| `GOOGLE_API_KEY` | No | - | Google Search API key |
| `GOOGLE_CSE_ID` | No | - | Google Custom Search Engine ID |

## Performance Characteristics
- **Startup time**: ~2-3 seconds
- **Memory usage**: ~50-100MB baseline
- **Response time**: Weather <2s, Search <3s
- **Concurrent requests**: 100+ with default settings