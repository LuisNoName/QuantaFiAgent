"""
Agent Backend - Main FastAPI service for routing requests to agents.

Receives AgentRequests from the Slack Backend, routes them to the appropriate
agent, and returns AgentResponses.
"""

import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from .models import AgentRequest, AgentResponse
from ..agents.engineer import Engineer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Agent Backend", version="1.0.0")

# Initialize the Engineer agent (in-memory, single instance)
engineer_agent = Engineer(name="engineer")


@app.get("/healthz")
async def healthcheck():
    """Health check endpoint."""
    return {"status": "ok", "service": "agent-backend"}


@app.post("/agent/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest) -> AgentResponse:
    """
    Main endpoint for processing agent requests.
    
    Receives an AgentRequest from the Slack Backend, routes it to the
    appropriate agent, and returns an AgentResponse.
    
    Args:
        request: AgentRequest containing message and context
        
    Returns:
        AgentResponse with the agent's reply
        
    Raises:
        HTTPException: If agent is not found or processing fails
    """
    try:
        # Extract request details for logging
        agent_name = request.agent.get("name", "unknown")
        channel = request.source.get("channel")
        username = request.source.get("username")
        message_text = request.message.get("text")
        
        # Log the incoming request
        logger.info(
            f"[INFO] Received message from {username} in {channel}: \"{message_text}\""
        )
        logger.info(f"Routing to agent: {agent_name}")
        
        # Route to the appropriate agent
        # For now, we only have the Engineer agent
        if agent_name == "engineer":
            response = engineer_agent.handle(request)
        else:
            logger.error(f"Unknown agent requested: {agent_name}")
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found"
            )
        
        # Log the response
        logger.info(
            f"Agent {agent_name} completed request {request.id} "
            f"with status: {response.agent.get('status')}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request {request.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error processing request: {str(e)}"
        )
