# This file is no longer strictly necessary if all logic is moved to FastMCP
# and tools are defined directly in main.py or a dedicated tools module
# that FastMCP can reference.

# However, if you plan to have complex tool definitions or shared logic
# for tool creation that FastMCP decorators alone don't cover, you might keep it.

# For now, let's assume it's not needed for the FastMCP refactor.
# You can delete this file if it becomes truly obsolete.

# Example of what might remain if you had custom Pydantic models for tool inputs:
# from pydantic import BaseModel, Field

# class WeatherInput(BaseModel):
#     location: str = Field(description="The city and state, e.g., San Francisco, CA")

# class SearchInput(BaseModel):
#     query: str = Field(description="The search query")

# These models could then be used as type hints in your FastMCP tool functions,
# and FastMCP would automatically generate the inputSchema from them.

# If MCPTool and MCPModel classes defined here were specific to your custom implementation
# and are now replaced by FastMCP, they can be removed.

# Original content commented out as it's replaced by FastMCP:
"""
import json
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

class MCPTool:
    def __init__(self, name: str, description: str, func: Callable, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.func = func
        self.input_schema = input_schema
        logger.debug(f"MCPTool initialized: {self.name} with schema {self.input_schema}")

    async def execute(self, params: Dict[str, Any]) -> Any:
        logger.info(f"Executing tool: {self.name} with params: {params}")
        # Assuming the underlying tool function (self.func) can be awaited if it's async
        # or called directly if it's sync. The `await` keyword handles both if `func` could be either.
        # However, for clarity, it's better if the nature of `func` (sync/async) is known.
        # If self.func is always synchronous:
        # return self.func(**params)
        # If self.func can be asynchronous:
        # For this example, let's assume they are synchronous as per current tool implementations
        try:
            result = self.func(**params)
            logger.info(f"Tool {self.name} execution successful, result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}", exc_info=True)
            # It's important to return an error structure that the MCP client expects
            # For now, re-raising or returning a simple error message
            # This should be refined based on MCP error reporting specs
            return {"error": str(e), "tool_name": self.name}

class MCPModel:
    def __init__(self, tools: List[MCPTool]):
        self.tools: Dict[str, MCPTool] = {tool.name: tool for tool in tools}
        logger.info(f"MCPModel initialized with tools: {list(self.tools.keys())}")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        method = request_data.get("method")
        params = request_data.get("params", {})
        request_id = request_data.get("id") # Get request_id for including in response

        logger.info(f"Processing request: method={method}, params={params}, id={request_id}")

        response: Dict[str, Any] = {"jsonrpc": "2.0"}
        if request_id is not None:
            response["id"] = request_id

        if method == "initialize":
            tool_defs = []
            for tool_name, tool_obj in self.tools.items():
                tool_defs.append({
                    "name": tool_obj.name,
                    "description": tool_obj.description,
                    "inputSchema": tool_obj.input_schema
                })
            response["result"] = {"toolDefinitions": tool_defs}
            logger.info(f"Initialize request processed. Tool definitions: {tool_defs}")
        elif method in self.tools:
            tool_to_run = self.tools[method]
            try:
                execution_result = await tool_to_run.execute(params)
                # Ensure the result is JSON serializable
                # The structure of the result should also align with MCP specs for tool calls
                response["result"] = execution_result 
                logger.info(f"Tool {method} executed. Result: {execution_result}")
            except Exception as e:
                logger.error(f"Error during tool execution for {method}: {e}", exc_info=True)
                response["error"] = {"code": -32000, "message": f"Error executing tool {method}: {str(e)}"}
        else:
            logger.warning(f"Unknown method: {method}")
            response["error"] = {"code": -32601, "message": "Method not found"}
        
        logger.debug(f"Sending response: {response}")
        return response
"""
