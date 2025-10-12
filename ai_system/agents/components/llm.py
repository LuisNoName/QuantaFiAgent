# LLM component
"""
LLM - OpenAI Chat API wrapper for generating agent responses.

Provides a simple interface to OpenAI's chat models (GPT-4, GPT-4o-mini, etc.)
for context-aware conversation generation.
"""

import logging
import os
from typing import List
from openai import OpenAI

from ...agent_backend.models import BasicMessage

logger = logging.getLogger(__name__)


class LLM:
    """
    Lightweight wrapper around OpenAI's Chat API.
    
    Supports models like:
    - gpt-4o-mini (default, cost-effective)
    - gpt-4o
    - gpt-4-turbo
    """

    def __init__(self, model_name: str = "gpt-4o-mini", use_flex: bool = True):
        """
        Initialize the LLM with OpenAI API credentials.
        
        Args:
            model_name: OpenAI model to use (default: gpt-4o-mini)
            
        Environment:
            OPENAI_API_KEY must be set in environment or .env file
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please add it to your .env file."
            )
        
        self.client = OpenAI(api_key=api_key)
        self.use_flex = use_flex
        self.model_name = model_name
        logger.info(f"Initialized LLM with model: {model_name}")

    def _format_messages(self, messages: List[BasicMessage]) -> str:
        """
        Format BasicMessage list into a single string for responses.create() API.
        
        Args:
            messages: List of BasicMessage objects
            
        Returns:
            Formatted conversation string
        """
        formatted = []
        for msg in messages:
            name_suffix = f" ({msg.name})" if msg.name else ""
            formatted.append(f"{msg.role.upper()}{name_suffix}: {msg.content}")
        return "\n".join(formatted)

    def chat(self, messages: List[BasicMessage]) -> str:
        """
        Send messages to OpenAI API and return the response.
        
        Args:
            messages: List of BasicMessage objects with role, content, and optional name
        
        Returns:
            The generated response text from the model
            
        Raises:
            Exception: If API call fails
        """
        try:
            logger.info(f"Calling OpenAI API with {len(messages)} messages")

            # Format messages into single input string
            input_text = self._format_messages(messages)

            if not self.use_flex:
                response = self.client.responses.create(
                    model=self.model_name,
                    input=input_text
                )
            else:
                response = self.client.with_options(timeout=900.0).responses.create(
                    model=self.model_name,
                    input=input_text,
                    service_tier="flex",
                )

            # ✅ Extract reply using new API helper
            reply = response.output_text.strip()

            # ✅ Usage stats
            tokens_used = response.usage.total_tokens if response.usage else Nonei

            logger.info(
                f"OpenAI response received: {len(reply)} chars, "
                f"{tokens_used or 'unknown'} tokens used"
            )

            return reply

            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}", exc_info=True)
            raise
