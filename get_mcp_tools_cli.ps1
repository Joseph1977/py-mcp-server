# MCP PowerShell Client using MCP CLI
# This script uses the official MCP CLI tool which properly handles the MCP protocol
param()

Write-Host "=== MCP PowerShell Client (CLI-based) ===" -ForegroundColor Magenta
Write-Host "Using official MCP CLI for proper protocol handling..." -ForegroundColor Green

# Check if Python virtual environment is active
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "`nERROR: Python not found. Please activate your virtual environment:" -ForegroundColor Red
    Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

# Check if MCP CLI is available
try {
    $mcpVersion = python -m mcp --version 2>&1
    Write-Host "MCP CLI found: $mcpVersion" -ForegroundColor Green
}
catch {
    Write-Host "`nERROR: MCP CLI not found. Installing..." -ForegroundColor Yellow
    pip install "mcp[cli]"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install MCP CLI" -ForegroundColor Red
        exit 1
    }
}

# Server URL
$serverUrl = "http://localhost:8001/mcp"

Write-Host "`nConnecting to MCP server at: $serverUrl" -ForegroundColor Yellow

try {
    # Test server connectivity first
    Write-Host "1. Testing server connectivity..." -ForegroundColor Yellow
    $healthCheck = Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET -ErrorAction Stop
    Write-Host "   SUCCESS: Server is running (HTTP $($healthCheck.StatusCode))" -ForegroundColor Green
    
    # Use MCP CLI to list tools
    Write-Host "`n2. Retrieving MCP tools using CLI..." -ForegroundColor Yellow
      # Create a temporary Python script to use MCP CLI programmatically
    $tempScript = @"
import asyncio
import sys
import json
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def get_tools():
    try:
        server_url = "$serverUrl"
        print(f"Connecting to {server_url}...")
        
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("SUCCESS: MCP session initialized")
                
                tools = await session.list_tools()
                print(f"\nMCP TOOLS LIST:")
                print("=" * 50)
                print(f"Found {len(tools.tools)} tools:\n")
                
                for i, tool in enumerate(tools.tools, 1):
                    print(f"{i}. {tool.name}")
                    print(f"   Description: {tool.description}")
                    
                    # Handle input schema properly
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        schema = tool.inputSchema
                        if hasattr(schema, 'properties') and schema.properties:
                            print("   Parameters:")
                            required_params = getattr(schema, 'required', [])
                            for param_name, param_def in schema.properties.items():
                                is_required = param_name in required_params
                                status = " (required)" if is_required else " (optional)"
                                
                                if hasattr(param_def, 'description'):
                                    desc = param_def.description
                                elif isinstance(param_def, dict) and 'description' in param_def:
                                    desc = param_def['description']
                                else:
                                    desc = f"Type: {getattr(param_def, 'type', 'unknown')}"
                                
                                print(f"     - {param_name}: {desc}{status}")
                        else:
                            print("   Parameters: None specified")
                    else:
                        print("   Parameters: None")
                    print()
                
                print(f"SUCCESS! Found {len(tools.tools)} working MCP tools")
                return 0
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(get_tools())
    sys.exit(exit_code)
"@

    # Write temporary script
    $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
    $tempScript | Out-File -FilePath $tempFile -Encoding UTF8
    
    # Execute the Python script
    python $tempFile
    $exitCode = $LASTEXITCODE
    
    # Clean up
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    
    if ($exitCode -eq 0) {
        Write-Host "`nSUCCESS: MCP tools retrieved successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Failed to retrieve MCP tools" -ForegroundColor Red
    }
}
catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Make sure MCP server is running: python run.py" -ForegroundColor White
    Write-Host "   2. Check server URL: $serverUrl" -ForegroundColor White
    Write-Host "   3. Verify port 8001 is not blocked" -ForegroundColor White
    Write-Host "   4. Try the Python client directly: python test_mcp_client.py" -ForegroundColor White
    Write-Host "   5. Activate virtual environment: .\.venv\Scripts\Activate.ps1" -ForegroundColor White
}

Write-Host "`nPowerShell MCP Client Complete!" -ForegroundColor Magenta
