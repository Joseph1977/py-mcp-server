#!/usr/bin/env python3
"""
Simple MCP client to test our server functionality
"""
import asyncio
import json
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def test_mcp_server():
    """Test the MCP server functionality"""
    server_url = "http://localhost:8001/mcp"
    
    try:
        print(f"Connecting to MCP server at {server_url}...")
        
        # Connect using streamable HTTP client
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                print("Initializing MCP session...")
                await session.initialize()
                print("✅ MCP session initialized successfully!")
                
                # List available tools
                print("\n📋 Listing available tools...")
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test calling a tool (weather)
                if tools.tools:
                    print(f"\n🔧 Testing weather tool...")
                    try:
                        result = await session.call_tool("weather", {"location": "San Francisco, CA"})
                        print(f"✅ Weather tool result: {result.content[0].text if result.content else 'No content'}")
                    except Exception as e:
                        print(f"❌ Weather tool error: {e}")
                    
                    # Test search tool
                    print(f"\n🔍 Testing brave search tool...")
                    try:
                        result = await session.call_tool("brave_search_tool", {"query": "MCP Model Context Protocol"})
                        print(f"✅ Search tool result: {result.content[0].text[:200] if result.content else 'No content'}...")
                    except Exception as e:
                        print(f"❌ Search tool error: {e}")
                
                # List available resources
                print(f"\n📚 Listing available resources...")
                resources = await session.list_resources()
                print(f"Found {len(resources.resources)} resources:")
                for resource in resources.resources:
                    print(f"  - {resource.uri}: {resource.name}")
                
                # List available prompts
                print(f"\n💬 Listing available prompts...")
                prompts = await session.list_prompts()
                print(f"Found {len(prompts.prompts)} prompts:")
                for prompt in prompts.prompts:
                    print(f"  - {prompt.name}: {prompt.description}")
                
                print(f"\n🎉 All tests completed successfully!")
                
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
