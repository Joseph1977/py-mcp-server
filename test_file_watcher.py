"""
Test client for File Watcher MCP Tools

This script demonstrates how to use the file watcher tools and SSE notifications.
"""
import asyncio
import json
import logging
import os
import tempfile
import time
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_file_watcher_tools():
    """Test the file watcher MCP tools."""
    print("🔧 Testing File Watcher MCP Tools...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test.txt"
        test_file2 = temp_path / "test.py"
        
        print(f"📁 Using test directory: {temp_dir}")
        
        # Start MCP client
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "app.main"],
            env={"MCP_TRANSPORT_MODE": "stdio"}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                # List available tools
                tools = await session.list_tools()
                print(f"📋 Available tools: {[tool.name for tool in tools.tools]}")
                
                # Test 1: Create file watcher
                print("\n🎯 Test 1: Creating file watcher...")
                watcher_id = "test_watcher_1"
                result = await session.call_tool(
                    "create_watcher",
                    arguments={
                        "watcher_id": watcher_id,
                        "watch_path": str(temp_dir),
                        "file_patterns": ["*.txt", "*.py"],
                        "exclude_patterns": ["*.tmp"],
                        "recursive": True,
                        "auto_start": True
                    }
                )
                print(f"✅ Create watcher result: {result.content[0].text}")
                
                # Test 2: List watchers
                print("\n🎯 Test 2: Listing watchers...")
                result = await session.call_tool("list_watchers_tool", arguments={})
                print(f"📋 Watchers list: {result.content[0].text}")
                
                # Test 3: Get watcher status
                print("\n🎯 Test 3: Getting watcher status...")
                result = await session.call_tool(
                    "get_watcher_status_tool",
                    arguments={"watcher_id": watcher_id}
                )
                print(f"📊 Watcher status: {result.content[0].text}")
                
                # Test 4: Create files to trigger events
                print("\n🎯 Test 4: Creating files to trigger events...")
                
                # Create first test file
                test_file.write_text("Hello, World!")
                print(f"📝 Created: {test_file}")
                
                # Wait a bit for events to be processed
                await asyncio.sleep(1)
                
                # Create second test file
                test_file2.write_text("print('Hello, Python!')")
                print(f"📝 Created: {test_file2}")
                
                # Modify first file
                test_file.write_text("Hello, Modified World!")
                print(f"✏️  Modified: {test_file}")
                
                # Wait for events
                await asyncio.sleep(2)
                
                # Test 5: Stop watcher
                print("\n🎯 Test 5: Stopping watcher...")
                result = await session.call_tool(
                    "stop_watcher_tool",
                    arguments={"watcher_id": watcher_id}
                )
                print(f"⏹️  Stop result: {result.content[0].text}")
                
                # Test 6: Create another watcher for specific files
                print("\n🎯 Test 6: Creating watcher for specific files...")
                watcher_id2 = "specific_file_watcher"
                result = await session.call_tool(
                    "create_watcher",
                    arguments={
                        "watcher_id": watcher_id2,
                        "watch_path": str(temp_dir),
                        "specific_files": [str(test_file)],
                        "auto_start": True
                    }
                )
                print(f"✅ Specific file watcher result: {result.content[0].text}")
                
                # Test 7: Modify specific file
                print("\n🎯 Test 7: Modifying specific watched file...")
                test_file.write_text("Specific file modification!")
                print(f"✏️  Modified specific file: {test_file}")
                
                await asyncio.sleep(1)
                
                # Test 8: Remove watchers
                print("\n🎯 Test 8: Removing watchers...")
                for wid in [watcher_id, watcher_id2]:
                    result = await session.call_tool(
                        "remove_watcher_tool",
                        arguments={"watcher_id": wid}
                    )
                    print(f"🗑️  Remove watcher '{wid}': {result.content[0].text}")
                
                # Final status check
                print("\n🎯 Final: Listing watchers after cleanup...")
                result = await session.call_tool("list_watchers_tool", arguments={})
                print(f"📋 Final watchers list: {result.content[0].text}")

async def test_sse_notifications():
    """Test SSE notifications for file watcher events."""
    print("\n🌐 Testing SSE Notifications...")
    
    # This test requires the server to be running in HTTP mode
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Check if server is running
            response = await client.get("http://localhost:8001/health")
            if response.status_code != 200:
                print("❌ Server not running in HTTP mode, skipping SSE test")
                return
            
            print("✅ Server is running, testing SSE...")
            
            # Create a temporary directory for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                test_file = temp_path / "sse_test.txt"
                
                print(f"📁 Using SSE test directory: {temp_dir}")
                
                # Start SSE connection in background
                sse_task = asyncio.create_task(monitor_sse_events())
                
                # Give SSE connection time to establish
                await asyncio.sleep(2)
                
                # Create watcher via HTTP API (if available) or skip
                print("📝 Creating files to test SSE notifications...")
                
                # Create and modify files
                test_file.write_text("SSE Test File")
                await asyncio.sleep(1)
                
                test_file.write_text("Modified SSE Test File")
                await asyncio.sleep(1)
                
                # Cancel SSE monitoring
                sse_task.cancel()
                
                try:
                    await sse_task
                except asyncio.CancelledError:
                    pass
    
    except Exception as e:
        print(f"❌ SSE test failed: {e}")
        print("💡 Tip: Start the server in HTTP mode first: python run.py")
        print("💡 Then run this test in a separate terminal to test SSE functionality")

async def monitor_sse_events():
    """Monitor SSE events from the file watcher."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("GET", "http://localhost:8001/file-watcher/sse") as response:
                print("🔄 Connected to SSE stream...")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            print(f"📡 SSE Event: {data}")
                        except json.JSONDecodeError:
                            print(f"📡 SSE Raw: {line}")
    except Exception as e:
        print(f"❌ SSE monitoring error: {e}")

async def main():
    """Main test function."""
    print("🚀 Starting File Watcher MCP Tools Test")
    print("=" * 50)
    
    try:
        # Test MCP tools
        await test_file_watcher_tools()
        
        # Test SSE notifications (requires HTTP server)
        await test_sse_notifications()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
