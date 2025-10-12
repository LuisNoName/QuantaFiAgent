"""Main Slack event processing gateway."""

import logging
from time import time
from typing import Any, Dict

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from slack_sdk import WebClient

from ...agent_backend.chat_history import ChatHistory
from ..utils.cache import EventCache
from .verifier import SlackRequestVerifier
from .normalizer import SlackEventNormalizer
from .agent_forwarder import AgentBackendClient
from .responder import SlackResponder

logger = logging.getLogger(__name__)


class SlackEventGateway:
    """
    Central orchestrator for Slack event processing.
    
    Coordinates verification, normalization, deduplication,
    and async processing of Slack events.
    """

    def __init__(
        self,
        slack_client: WebClient,
        signing_secret: str,
        agent_backend_url: str,
        bot_user_id: str
    ):
        """
        Initialize the gateway with all dependencies.
        
        Args:
            slack_client: Configured Slack WebClient
            signing_secret: Slack app signing secret
            agent_backend_url: URL of the Agent Backend
            bot_user_id: Slack bot user ID for mention detection
        """
        # Initialize components
        self.verifier = SlackRequestVerifier(signing_secret)
        self.normalizer = SlackEventNormalizer(slack_client)
        self.forwarder = AgentBackendClient(agent_backend_url)
        self.responder = SlackResponder(slack_client)
        
        # Initialize utilities
        self.event_cache = EventCache(ttl_seconds=300)
        self.chat_history = ChatHistory()
        
        # Store configuration
        self.slack_client = slack_client
        self.bot_user_id = bot_user_id
        
        # Setup FastAPI router
        self.router = APIRouter()
        self.router.add_api_route("/slack/events", self.handle_event, methods=["POST"])
        self.router.add_api_route("/healthz", self.healthcheck, methods=["GET"])

    async def healthcheck(self):
        """Health check endpoint."""
        return {"status": "ok", "service": "slack-backend"}

    async def handle_event(self, request: Request, background_tasks: BackgroundTasks):
        """
        Main endpoint for receiving Slack Events API callbacks.
        
        Handles signature verification, deduplication, and async processing.
        """
        # Get headers and body
        headers = request.headers
        body_bytes = await request.body()
        body = await request.json()

        # Verify Slack signature
        timestamp = headers.get("X-Slack-Request-Timestamp", "")
        signature = headers.get("X-Slack-Signature", "")

        if not self.verifier.verify(body_bytes, timestamp, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle URL verification challenge
        if body.get("type") == "url_verification":
            logger.info("Responding to URL verification challenge")
            return {"challenge": body.get("challenge")}

        # Handle event callback
        if body.get("type") == "event_callback":
            event = body.get("event", {})
            event_type = event.get("type")
            event_ts = event.get("ts")
            event_id = f"{event_type}:{event_ts}"

            logger.info(f"Received event type: {event_type}, ts: {event_ts}")

            # Check if event is too old
            event_age = time() - float(event_ts)
            if event_age > 60:  # 60 seconds - only process fresh events
                logger.info(f"⏰ IGNORING OLD EVENT - {event_age:.1f}s old (threshold: 60s)")
                return {"ok": True}

            # Check for duplicates
            if self.event_cache.has_event(event_id):
                age = self.event_cache.get_age(event_id)
                logger.info(f"🔄 DUPLICATE EVENT - processed {age:.1f}s ago")
                return {"ok": True}

            # Mark as processed
            self.event_cache.add_event(event_id)
            logger.info(f"✨ New event (age: {event_age:.1f}s)")

            # Ignore bot messages
            if event.get("subtype") == "bot_message" or event.get("bot_id"):
                logger.info("Ignoring bot message")
                return {"ok": True}

            # Skip message events with mentions (handled by app_mention)
            if event_type == "message":
                text = event.get("text", "")
                if self.bot_user_id and f"<@{self.bot_user_id}>" in text:
                    logger.info("🚫 SKIPPING message event with bot mention")
                    return {"ok": True}

            # Determine if we should respond
            should_respond = self._should_respond(event, event_type)

            # Process asynchronously
            if event_type in ["app_mention", "message"]:
                background_tasks.add_task(
                    self._process_event_async,
                    event=event,
                    event_type=event_type,
                    should_respond=should_respond
                )
                logger.info("⚡ Acknowledged event, processing in background")
                return {"ok": True}

        # Unknown request type
        logger.warning(f"Unknown request type: {body.get('type')}")
        return {"ok": True}

    def _should_respond(self, event: Dict[str, Any], event_type: str) -> bool:
        """
        Determine if we should respond to this event.
        
        Args:
            event: Slack event dictionary
            event_type: Type of event (app_mention, message, etc.)
            
        Returns:
            True if we should generate a response, False otherwise
        """
        if event_type == "app_mention":
            logger.info("Bot mentioned - will respond")
            return True
        elif event_type == "message":
            channel_type = event.get("channel_type")
            if channel_type in ["im", "mpim"]:
                logger.info("DM received - will respond")
                return True
            else:
                logger.info("Regular message - context only")
                return False
        return False

    async def _process_event_async(
        self,
        event: Dict[str, Any],
        event_type: str,
        should_respond: bool
    ):
        """
        Process event asynchronously (runs in background).
        
        Args:
            event: Slack event dictionary
            event_type: Type of event
            should_respond: Whether to generate and post a response
        """
        try:
            conversation_id = f"{event['channel']}:{event.get('thread_ts', event['ts'])}"
            
            # Get username
            try:
                user_info = self.slack_client.users_info(user=event["user"])
                username = user_info["user"]["name"]
            except Exception as e:
                logger.error(f"Failed to fetch user info: {e}")
                username = event.get("user", "unknown")

            # Clean text
            text = event.get("text", "")
            clean_text = self.normalizer._clean_bot_mentions(text)

            # Save to chat history
            self.chat_history.append(
                conversation_id,
                "user",
                name=username,
                content=clean_text
            )
            logger.info(f"Saved message from {username}")

            # Generate response if needed
            if should_respond:
                logger.info(f"🤖 Forwarding to Agent Backend")
                
                # Normalize event
                agent_request = self.normalizer.normalize(event)
                
                # Forward to agent backend
                agent_response = self.forwarder.forward_request(agent_request)
                
                # Post response to Slack
                self.responder.post_message(agent_response)
                
                logger.info(f"✅ Response posted for {conversation_id}")
            else:
                logger.info(f"💾 Context saved only")

        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)

