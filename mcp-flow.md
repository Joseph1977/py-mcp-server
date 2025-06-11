# MCP Client Developer Guide - Communication Flow

This document explains the Model Context Protocol (MCP) from a **CLIENT DEVELOPER** perspective. It shows exactly what headers to send, what responses to expect, and how to handle session management when building MCP clients.

## MCP Client Communication Flow

Here's the complete protocol flow from a client developer's perspective:

| Step | Client Action | HTTP Method | Endpoint | Required Headers | Request Body | Expected Response | What to Extract | Next Step |
|------|---------------|-------------|----------|------------------|--------------|-------------------|----------------|-----------|
| 0 | **Health Check** | **GET** | `/health` | None | None | JSON status | Server health status | Verify server is running |
| 1 | **Initialize** | **POST** | `/mcp` | `Content-Type: application/json`<br>`Accept: application/json, text/event-stream` | JSON-RPC `initialize` method | JSON-RPC response with capabilities | **Extract `sessionId` from response** | Use sessionId in all future requests |
| 2 | **List Tools** | **POST** | `/mcp` | `Content-Type: application/json`<br>`Accept: application/json, text/event-stream`<br>**`MCP-Session-Id: <extracted-session-id>`** | JSON-RPC `tools/list` method | JSON-RPC response with tools array | Tool definitions and schemas | Store available tools |
| 3 | **Call Tool** | **POST** | `/mcp` | `Content-Type: application/json`<br>`Accept: application/json, text/event-stream`<br>**`MCP-Session-Id: <extracted-session-id>`** | JSON-RPC `tools/call` with parameters | JSON-RPC response with results | Tool execution results | Process results |
| 4 | **List Resources** | **POST** | `/mcp` | `Content-Type: application/json`<br>`Accept: application/json, text/event-stream`<br>**`MCP-Session-Id: <extracted-session-id>`** | JSON-RPC `resources/list` method | JSON-RPC response with resources | Available resources list | Store resources |
| 5 | **List Prompts** | **POST** | `/mcp` | `Content-Type: application/json`<br>`Accept: application/json, text/event-stream`<br>**`MCP-Session-Id: <extracted-session-id>`** | JSON-RPC `prompts/list` method | JSON-RPC response with prompts | Available prompts list | Store prompts |

## Client Session Management Requirements

### Step 0: Health Check (Optional but Recommended)
**Client sends:** **GET** request to `/health` endpoint WITHOUT any special headers  
**Server responds:** JSON status object  
**Client should:** Verify server is running before attempting MCP protocol

### Step 1: Initialize (No Session Header)
**Client sends:** **POST** request to `/mcp` endpoint with initialize method WITHOUT session header  
**Server responds:** Capabilities + session ID  
**Client must:** Extract and store the session ID for all future requests

### Steps 2-5: All MCP Protocol Requests (Session Header Required)
**Client sends:** **POST** requests to `/mcp` endpoint WITH `MCP-Session-Id` header  
**Server responds:** Requested data  
**Client must:** Always include the session ID from step 1

**Important**: 
- **GET requests**: Used for server information (`/health`, `/info`) - no session needed
- **POST requests**: Used for MCP protocol (`/mcp`) - session required after initialize

## Client Request/Response Examples

### 1. Initialize Request (Client Perspective)
**What client sends:**
```http
POST /mcp HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

**What client receives:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {}
    },
    "serverInfo": {
      "name": "Benraz-MCP-Server",
      "version": "1.0.0"
    },
    "sessionId": "mcp-session-abc123-def456"
  }
}
```

**What client must do:** Extract `sessionId` value and use it in all subsequent requests.

### 2. Tools List Request (Client Perspective)
**What client sends:**
```http
POST /mcp HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Session-Id: mcp-session-abc123-def456

{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**What client receives:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "weather",
        "description": "Get weather information",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City and state"
            }
          },
          "required": ["location"]
        }
      }
    ]
  }
}
```

### 3. Tool Call Request (Client Perspective)
**What client sends:**
```http
POST /mcp HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream
MCP-Session-Id: mcp-session-abc123-def456

{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "weather",
    "arguments": {
      "location": "San Francisco, CA"
    }
  }
}
```

**What client receives:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Current weather in San Francisco, CA: 72°F, partly cloudy"
      }
    ],
    "isError": false
  }
}
```

## Client Developer Checklist

### Essential Client Implementation Steps:

1. **Send Initialize Request**
   - ✅ Include `Content-Type: application/json` header
   - ✅ Include `Accept: application/json, text/event-stream` header  
   - ✅ Do NOT include session header in initialize request

2. **Handle Initialize Response**
   - ✅ Extract `sessionId` from response JSON
   - ✅ Store session ID for all future requests
   - ✅ Parse server capabilities to know what features are available

3. **Send All Other Requests**
   - ✅ Include `Content-Type: application/json` header
   - ✅ Include `Accept: application/json, text/event-stream` header
   - ✅ Include `MCP-Session-Id: <extracted-session-id>` header
   - ✅ Use session ID from initialize response

4. **Error Handling**
   - ✅ Handle JSON-RPC error responses
   - ✅ Handle HTTP error status codes  
   - ✅ Handle network connectivity issues

### Common Client Mistakes to Avoid:

❌ **DON'T** send session header with initialize request  
❌ **DON'T** forget to extract session ID from initialize response  
❌ **DON'T** send requests without session header (except initialize)  
❌ **DON'T** assume server will work without proper headers

## Client Implementation Examples

### PowerShell Client (Raw HTTP)
```powershell
# Step 0: Check server health (optional)
$healthResponse = Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET
Write-Host "Server Status: $($healthResponse.StatusCode)"

# Step 1: Initialize (no session header)
$headers = @{
    'Content-Type' = 'application/json'
    'Accept' = 'application/json, text/event-stream'
}
$initBody = @{
    jsonrpc = "2.0"
    id = 1
    method = "initialize"
    params = @{
        protocolVersion = "2024-11-05"
        capabilities = @{}
        clientInfo = @{
            name = "powershell-client"
            version = "1.0.0"
        }
    }
} | ConvertTo-Json -Depth 5

$response = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $headers -Body $initBody
$initResult = ($response.Content | ConvertFrom-Json).result

# Step 2: Extract session ID
$sessionId = $initResult.sessionId

# Step 3: Use session ID for all other MCP requests
$headers['MCP-Session-Id'] = $sessionId
$toolsBody = @{
    jsonrpc = "2.0"
    id = 2
    method = "tools/list"
    params = @{}
} | ConvertTo-Json

$toolsResponse = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $headers -Body $toolsBody
```

### Python Client (Raw HTTP)
```python
import requests
import json

# Step 0: Check server health (optional)
health_response = requests.get('http://localhost:8001/health')
print(f"Server Status: {health_response.status_code}")

# Step 1: Initialize (no session header)
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'
}

init_data = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "python-client",
            "version": "1.0.0"
        }
    }
}

response = requests.post('http://localhost:8001/mcp', headers=headers, json=init_data)
init_result = response.json()['result']

# Step 2: Extract session ID
session_id = init_result['sessionId']

# Step 3: Use session ID for all other MCP requests
headers['MCP-Session-Id'] = session_id

tools_data = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}

tools_response = requests.post('http://localhost:8001/mcp', headers=headers, json=tools_data)
tools = tools_response.json()['result']['tools']
```

## Error Handling (Client Perspective)

### Standard JSON-RPC Errors
When the server returns an error, clients receive this format:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": "Additional error details"
  }
}
```

### Common Error Codes:
- `-32700`: Parse error - Client sent invalid JSON
- `-32600`: Invalid Request - Missing required fields
- `-32601`: Method not found - Unknown method name
- `-32602`: Invalid params - Wrong parameters for method
- `-32603`: Internal error - Server-side issue

### HTTP Status Errors:
- `401 Unauthorized`: Missing or invalid session ID
- `404 Not Found`: Wrong endpoint URL
- `500 Internal Server Error`: Server-side problem

### Client Error Handling Strategy:
```python
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Handle HTTP errors
    
    result = response.json()
    if 'error' in result:
        # Handle JSON-RPC errors
        print(f"MCP Error {result['error']['code']}: {result['error']['message']}")
    else:
        # Process successful result
        return result['result']
except requests.exceptions.RequestException as e:
    # Handle network/HTTP errors
    print(f"Network error: {e}")
```

## Summary for Client Developers

**The MCP protocol from a client perspective:**

1. **Health Check**: Send **GET** request to `/health` → Verify server is running (optional)
2. **Initialize**: Send **POST** request to `/mcp` with initialize → Get session ID back
3. **Use Session ID**: Include session ID in ALL subsequent **POST** request headers to `/mcp`  
4. **Make Requests**: Call tools, list resources, etc. with proper session header using **POST** to `/mcp`
5. **Handle Errors**: Check for JSON-RPC errors and HTTP status codes

**Key Takeaways**: 
- **GET requests**: Used for server info (`/health`, `/info`) - no session needed
- **POST requests**: Used for MCP protocol (`/mcp`) - session required after initialize
- The session ID is YOUR responsibility as a client developer. Extract it from the initialize response and include it in every subsequent MCP request header.
