# MCP component
from typing import Dict, Callable
from ...agent_backend.models import ToolCall, ToolResult


class MCP:
    """
    Provides callable tools that the agent can use to perform actions.
    Each tool is a function registered in a central registry.
    """

    def __init__(self):
        self.tools: Dict[str, Callable[..., ToolResult]] = {}

    def register_tool(self, name: str, func: Callable[..., ToolResult]) -> None:
        """Register a callable tool."""

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call safely (with error handling and logging).
        """
