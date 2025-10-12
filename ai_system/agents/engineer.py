"""
Engineer Agent - Context-aware conversational agent with LLM integration.

Uses ChatHistory for persistent conversation storage and OpenAI's GPT models
for generating intelligent, context-aware responses.
"""

import logging
from ..agent_backend.models import AgentRequest, AgentResponse
from ..agent_backend.chat_history import ChatHistory
from .components.llm import LLM

logger = logging.getLogger(__name__)


class Engineer:
    """
    Engineer agent with conversation memory and LLM-powered responses.
    
    Features:
    - Persistent per-thread conversation history
    - Context-aware responses using OpenAI GPT models
    - Maintains conversation continuity across multiple interactions
    """

    def __init__(self, name: str = "engineer", model_name: str = "gpt-5-nano"):
        """
        Initialize the Engineer agent with ChatHistory and LLM components.
        
        Args:
            name: Agent name (default: "engineer")
            model_name: OpenAI model to use (default: "gpt-4o-mini")
        """
        self.name = name
        self.chat_history = ChatHistory()
        self.llm = LLM(model_name=model_name, use_flex=True)
        logger.info(f"Initialized Engineer agent: {self.name} with model {model_name}")

    def handle(self, request: AgentRequest) -> AgentResponse:
        """
        Process an AgentRequest with full conversation context.
        
        Workflow:
        1. Extract conversation_id and user message
        2. Append user message to chat history
        3. Load full conversation history
        4. Generate LLM response with full context
        5. Append LLM response to chat history
        6. Return AgentResponse
        
        Args:
            request: AgentRequest from Slack Backend

        Returns:
            AgentResponse with LLM-generated reply
        """
        # Extract request information
        conversation_id = request.context.get("conversation_id")
        channel = request.source.get("channel")
        thread_ts = request.source.get("thread_ts")
        username = request.source.get("username")
        user_text = request.message.get("text")

        # Log the incoming request
        logger.info(
            f"Processing message from {username} in conversation {conversation_id}: "
            f"\"{user_text[:50]}...\""
        )

        try:
            # NOTE: User message is already saved by Slack Backend
            # We just need to load history, generate response, and save assistant's reply
            
            # 1. Load full conversation history (includes the user's message)
            messages = self.chat_history.load(conversation_id)
            logger.info(f"Loaded {len(messages)} messages from conversation history")

            # 2. Generate LLM response with full conversation context
            reply_text = self.llm.chat(messages)
            logger.info(f"Generated LLM response: {len(reply_text)} chars")

            # 3. Append only the assistant's response to chat history
            # Include agent name for multi-agent scenarios
            self.chat_history.append(conversation_id, "assistant", name=self.name, content=reply_text)
            logger.info(f"Appended {self.name} response to history")

            # 5. Create and return AgentResponse
            response = AgentResponse(
                id=request.id,
                agent={
                    "name": self.name,
                    "status": "completed"
                },
                reply={
                    "text": reply_text,
                    "channel": channel,
                    "thread_ts": thread_ts
                },
                meta={
                    "conversation_id": conversation_id,
                    "message_count": len(messages) + 1
                }
            )

            logger.info(f"Successfully processed request {request.id}")
            return response

        except Exception as e:
            logger.error(f"Error processing request {request.id}: {e}", exc_info=True)
            
            # Return error response
            error_response = AgentResponse(
                id=request.id,
                agent={
                    "name": self.name,
                    "status": "error"
                },
                reply={
                    "text": f"Sorry, I encountered an error processing your message: {str(e)}",
                    "channel": channel,
                    "thread_ts": thread_ts
                },
                meta={"error": str(e)}
            )
            
            return error_response

