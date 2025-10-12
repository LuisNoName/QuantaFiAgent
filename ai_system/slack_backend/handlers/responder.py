"""Slack message posting."""

import logging
from typing import Dict, Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackResponder:
    """
    Sends messages back to Slack.
    
    Wraps Slack WebClient with error handling and logging.
    """

    def __init__(self, slack_client: WebClient):
        """
        Initialize the responder with a Slack client.
        
        Args:
            slack_client: Configured Slack WebClient instance
        """
        self.slack_client = slack_client

    def post_message(self, agent_response: Dict[str, Any]) -> None:
        """
        Post an agent response back to Slack.
        
        Args:
            agent_response: AgentResponse dictionary with reply details
            
        Raises:
            SlackApiError: If posting to Slack fails
        """
        reply = agent_response.get("reply", {})
        channel = reply.get("channel")
        thread_ts = reply.get("thread_ts")
        text = reply.get("text", "")

        try:
            self.slack_client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=text
            )
            logger.info(f"Posted reply to Slack - Channel: {channel}, Thread: {thread_ts}")
            
        except SlackApiError as e:
            logger.error(f"Failed to post message to Slack: {e}")
            raise

