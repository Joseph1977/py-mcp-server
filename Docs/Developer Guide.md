# Developer Guide

## 🚀 Quick Development Setup

```bash
# 1. Environment setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate     # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start development server
python run.py
```

## 🧪 Testing Strategy

### Manual Testing
```bash
# Test all tools
python test_mcp_client.py

# Test specific endpoints
curl http://localhost:8001/health
curl http://localhost:8001/info
```

### PowerShell Testing (Windows)
```powershell
powershell -ExecutionPolicy Bypass -File "get_mcp_tools_cli.ps1"
```

## 🔧 Adding New Tools

### Step 1: Create Tool Implementation
```python
# app/tools/my_tool.py
async def my_tool_function(param: str) -> dict:
    """Your tool implementation"""
    return {"result": f"Processed: {param}"}
```

### Step 2: Register in Main App
```python
# In app/main.py
from app.tools.my_tool import my_tool_function

@mcp_server.tool()
async def my_tool(param: str) -> str:
    """Tool description for MCP"""
    result = await my_tool_function(param)
    return str(result)
```

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port 8001 in use | Change `MCP_SERVER_PORT` in `.env` |
| Import errors | Activate virtual environment |
| API key errors | Add valid keys to `.env` file |
| Docker issues | Check Docker daemon is running |