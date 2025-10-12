"""Agent Backend HTTP client."""

import logging
from typing import Dict, Any

import requests
from fastapi import HTTPException

from ...agent_backend.models import AgentRequest

logger = logging.getLogger(__name__)


class AgentBackendClient:
    """
    Handles HTTP communication with the Agent Backend.
    
    Encapsulates retry and timeout logic for agent requests.
    """

    def __init__(self, backend_url: str, timeout: int = 120):
        """
        Initialize the client with backend URL.
        
        Args:
            backend_url: Base URL of the Agent Backend
            timeout: Request timeout in seconds (default: 2 minutes)
        """
        self.backend_url = backend_url
        self.timeout = timeout

    def forward_request(self, agent_request: AgentRequest) -> Dict[str, Any]:
        """
        Forward an AgentRequest to the Agent Backend.
        
        Args:
            agent_request: Normalized agent request
            
        Returns:
            AgentResponse as dictionary
            
        Raises:
            HTTPException: If backend request fails
        """
        url = f"{self.backend_url}/agent/invoke"

        try:
            response = requests.post(
                url,
                json=agent_request.model_dump(),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to forward request to agent backend: {e}")
            raise HTTPException(
                status_code=502,
                detail=f"Agent backend unavailable: {str(e)}"
            )

