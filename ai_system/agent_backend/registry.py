# ThreadRegistry management
from typing import Dict, Optional


class ThreadRegistry:
    """
    Manages mapping between conversation IDs and agent threads.
    Tracks which agent is handling which conversation.
    """

    def __init__(self):
        self.registry: Dict[str, str] = {}  # conversation_id -> agent_name

    def register(self, conversation_id: str, agent_name: str) -> None:
        """Register a conversation to an agent."""
        self.registry[conversation_id] = agent_name

    def get_agent(self, conversation_id: str) -> Optional[str]:
        """Get the agent assigned to a conversation."""
        return self.registry.get(conversation_id)

    def unregister(self, conversation_id: str) -> None:
        """Remove a conversation from the registry."""
        if conversation_id in self.registry:
            del self.registry[conversation_id]

