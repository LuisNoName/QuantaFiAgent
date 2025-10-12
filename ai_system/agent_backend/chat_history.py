# Persistent conversation store
"""
ChatHistory - JSONL-based persistent storage for per-thread conversations.

Each conversation (Slack thread) is stored in a separate JSONL file:
chat_history/{conversation_id}.jsonl

Messages are stored in OpenAI Chat API format:
{"role": "user", "content": "..."}
{"role": "assistant", "content": "..."}
"""

import json
import os
from typing import List
from .models import BasicMessage


class ChatHistory:
    """
    File-based conversation storage using JSONL format.
    Each conversation_id (channel:thread_ts) gets its own file.
    """

    def __init__(self, base_path: str = "chat_history"):
        """
        Initialize ChatHistory with a base directory for storing conversations.
        
        Args:
            base_path: Directory path where conversation files will be stored
            mode: Mode of the chat history (BaseMessage or Message)
        """
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _path(self, conversation_id: str) -> str:
        """
        Generate the file path for a conversation.
        
        Args:
            conversation_id: Unique conversation identifier (e.g., "C12345:1234567890.123456")
            
        Returns:
            Full file path for the conversation JSONL file
        """
        # Sanitize conversation_id for filesystem (replace : with _)
        safe_id = conversation_id.replace(":", "_")
        return os.path.join(self.base_path, f"{safe_id}.jsonl")

    def append(self, conversation_id: str, role: str, content: str, name: str = None) -> None:
        """
        Append a message to the conversation history.
        
        Args:
            conversation_id: Unique conversation identifier
            role: Message role ("user" or "assistant")
            content: Message text content
            name: Optional name of the message author (username or agent name)
        """
        path = self._path(conversation_id)
        with open(path, "a", encoding="utf-8") as f:
            message = {"role": role}
            if name:
                message["name"] = name.replace(".", "_").replace("-", "_")  # OpenAI requires alphanumeric + underscore
            if content:
                message["content"] = content
            f.write(json.dumps(message) + "\n")

    def load(self, conversation_id: str) -> List[BasicMessage]:
        """
        Load all messages from a conversation in chronological order.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            List of BasicMessage objects with role, content, and optional name
        """
        path = self._path(conversation_id)
        if not os.path.exists(path):
            return []
        
        messages = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    messages.append(BasicMessage(**data))
        
        return messages

