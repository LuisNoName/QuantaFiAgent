# Base Agent orchestration
from typing import List
from ..agent_backend.models import (
    AgentRequest,
    AgentResponse,
    ContextBundle,
    ToolCall,
    ToolResult,
    LLMResponse,
)
from .components.chat_history import ChatHistory
from .components.short_term_memory import ShortTermMemory
from .components.long_term_memory import LongTermMemory
from .components.llm import LLM
from .components.mcp import MCP


class Agent:
    """
    The central orchestrator that maintains state, handles messages,
    and coordinates between memory, LLM, and MCP tools.
    """

    def __init__(
        self,
        name: str,
        chat_history: ChatHistory,
        short_term_memory: ShortTermMemory,
        long_term_memory: LongTermMemory,
        llm: LLM,
        mcp: MCP,
    ):
        self.name = name
        self.chat_history = chat_history
        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory
        self.llm = llm
        self.mcp = mcp

    # === High-level lifecycle ===
    def handle(self, request: AgentRequest) -> AgentResponse:
        """
        Entry point for handling a request (from AgentBackend).
        - Logs the message
        - Updates context
        - Generates a response
        - Returns AgentResponse
        """
        ...

    # === Internal steps ===
    def _build_context(self, conversation_id: str) -> ContextBundle:
        """
        Combine recent chat history, relevant long-term memory, and
        current objective into a ContextBundle for the LLM.
        """
        ...

    def _generate_reply(self, context: ContextBundle) -> LLMResponse:
        """
        Query the LLM with the given context and return its response.
        May include tool calls.
        """
        ...

    def _execute_tools(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """
        Execute any requested MCP tools and return results.
        """
        ...

    def _finalize_response(
        self, llm_response: LLMResponse, tool_results: List[ToolResult]
    ) -> AgentResponse:
        """
        Build and return the final AgentResponse to send back to Slack.
        """
        ...
