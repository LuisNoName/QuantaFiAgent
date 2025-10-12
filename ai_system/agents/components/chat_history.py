# Chat history component
from typing import List
from ...agent_backend.models import Message, ConversationRecord


class ChatHistory:
    """
    Persistent conversation log for a specific agent.
    Provides methods to append, retrieve, and summarize messages.
    """

    def append(self, message: Message) -> None:
        """Store a new message (human or bot)."""

    def get_recent(
        self, conversation_id: str, n: int = 10
    ) -> List[Message]:
        """Return the last N messages from a conversation."""

    def summarize(
        self, conversation_id: str
    ) -> str:
        """Summarize long conversations (for use in ShortTermMemory)."""

    def load_conversation(
        self, conversation_id: str
    ) -> ConversationRecord:
        """Return all stored messages for a conversation."""
