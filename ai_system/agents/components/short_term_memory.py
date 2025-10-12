# Short-term memory component
from typing import List, Optional
from ...agent_backend.models import Message, ContextBundle


class ShortTermMemory:
    """
    Builds the immediate working context for the LLM from
    chat history, task state, and retrieved long-term memory.
    """

    def build_context(
        self,
        conversation_id: str,
        recent_messages: List[Message],
        retrieved_knowledge: List[str],
        current_objective: Optional[str] = None,
    ) -> ContextBundle:
        """Combine data into a unified ContextBundle for LLM input."""
