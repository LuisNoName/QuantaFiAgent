# Long-term memory component
from typing import List, Optional
from ...agent_backend.models import ConversationRecord


class LongTermMemory:
    """
    Persistent knowledge store.
    Starts as a simple text file or key-value map, later becomes a vector store.
    """

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """
        Retrieve the top-k relevant memory entries for the query.
        Simple keyword search for now.
        """

    def add_entry(self, text: str, metadata: Optional[dict] = None) -> None:
        """Add new knowledge to the memory store."""

    def summarize_and_store_conversation(self, record: ConversationRecord) -> None:
        """(Future) Periodic learning step: summarize past conversations."""
