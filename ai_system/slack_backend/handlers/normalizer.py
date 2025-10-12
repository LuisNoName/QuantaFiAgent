"""Slack event normalization to AgentRequest format."""

import logging
import re
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from ...agent_backend.models import AgentRequest

logger = logging.getLogger(__name__)


class SlackEventNormalizer:
    """
    Converts Slack events into AgentRequest objects.
    
    Handles text cleaning, mention removal, and username fetching.
    """

    def __init__(self, slack_client: WebClient):
        """
        Initialize the normalizer with a Slack client.
        
        Args:
            slack_client: Configured Slack WebClient instance
        """
        self.slack_client = slack_client

    def normalize(self, event: Dict[str, Any]) -> AgentRequest:
        """
        Convert a Slack event to an AgentRequest.
        
        Args:
            event: Slack event dictionary
            
        Returns:
            AgentRequest object ready to send to Agent Backend
        """
        # Get username
        username = self._fetch_username(event.get("user"))
        
        # Clean message text
        raw_text = event.get("text", "")
        clean_text = self._clean_bot_mentions(raw_text)
        
        # Build conversation ID
        thread_ts = event.get("thread_ts", event["ts"])
        conversation_id = f"{event['channel']}:{thread_ts}"
        
        # Create AgentRequest
        return AgentRequest(
            id=str(uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            source={
                "platform": "slack",
                "workspace": event.get("team", "unknown"),
                "channel": event["channel"],
                "thread_ts": thread_ts,
                "user_id": event["user"],
                "username": username
            },
            agent={"name": "engineer", "type": "developer"},
            message={
                "text": clean_text,
                "raw_text": raw_text
            },
            context={"conversation_id": conversation_id}
        )

    def _fetch_username(self, user_id: str) -> str:
        """
        Fetch username from Slack API.
        
        Args:
            user_id: Slack user ID
            
        Returns:
            Username or "unknown" if fetch fails
        """
        try:
            user_info = self.slack_client.users_info(user=user_id)
            return user_info["user"]["name"]
        except SlackApiError as e:
            logger.error(f"Failed to fetch user info for {user_id}: {e}")
            return "unknown"

    @staticmethod
    def _clean_bot_mentions(text: str) -> str:
        """
        Remove bot mention tags from text.
        
        Args:
            text: Raw message text with potential <@UXXXX> mentions
            
        Returns:
            Cleaned text without bot mentions
        """
        return re.sub(r'<@[A-Z0-9]+>', '', text).strip()

