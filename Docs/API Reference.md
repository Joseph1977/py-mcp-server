# API Reference

## MCP Tools

### Weather Tool
```json
{
  "name": "weather",
  "description": "Get weather information for a location",
  "parameters": {
    "location": {
      "type": "string",
      "description": "City and state, e.g., 'San Francisco, CA'",
      "required": true
    }
  }
}
```

### Search Tools
```json
{
  "name": "brave_search_tool",
  "description": "Search the web using Brave Search",
  "parameters": {
    "query": {
      "type": "string",
      "description": "Search query",
      "required": true
    },
    "count": {
      "type": "integer",
      "description": "Number of results (default: 10)",
      "required": false
    },
    "sites": {
      "type": "array",
      "description": "Restrict search to specific sites",
      "required": false
    }
  }
}
```

## REST Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/health` | GET | Server health check | `{"status": "healthy"}` |
| `/info` | GET | Server information | Server details object |
| `/mcp` | POST/SSE | MCP protocol endpoint | MCP responses |