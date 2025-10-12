"""
Slack Backend - Minimal, class-based event processing gateway.

This is the main entry point. All business logic lives in handlers/.
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from slack_sdk import WebClient

from .handlers import SlackEventGateway

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration from environment
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
AGENT_BACKEND_URL = os.getenv("AGENT_BACKEND_URL", "http://localhost:8000")

# Initialize Slack client
slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Get bot user ID
try:
    bot_user_id = slack_client.auth_test()["user_id"]
    logger.info(f"Bot user ID: {bot_user_id}")
except Exception as e:
    logger.error(f"Failed to get bot user ID: {e}")
    bot_user_id = None

# Initialize gateway with all dependencies
gateway = SlackEventGateway(
    slack_client=slack_client,
    signing_secret=SLACK_SIGNING_SECRET,
    agent_backend_url=AGENT_BACKEND_URL,
    bot_user_id=bot_user_id
)

# Create FastAPI app
app = FastAPI(title="Slack Backend", version="2.0")

# Register routes
app.include_router(gateway.router)

logger.info("Slack Backend initialized successfully")
