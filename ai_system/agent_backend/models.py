# Pydantic data contracts
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class Message(BaseModel):
    id: str
    platform: str               # e.g. "slack"
    workspace: str
    channel: str
    thread_ts: str
    conversation_id: str        # channel:thread_ts
    user_id: str
    username: str
    is_bot: bool = False
    agent: Optional[str] = None
    text: str
    raw_text: Optional[str] = None
    timestamp: datetime
    metadata: dict = Field(default_factory=dict)

class BasicMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ConversationRecord(BaseModel):
    conversation_id: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    participants: List[str] = Field(default_factory=list)
    agent: Optional[str] = None

class ContextBundle(BaseModel):
    conversation_id: str
    recent_messages: List[Message]
    retrieved_knowledge: List[str] = Field(default_factory=list)
    current_objective: Optional[str] = None

class AgentRequest(BaseModel):
    id: str
    timestamp: str               # ISO 8601 datetime string
    source: dict                 # { platform, workspace, channel, thread_ts, user_id, username }
    agent: dict                  # { name, type }
    message: dict                # { text, raw_text }
    context: dict = Field(default_factory=dict)

class AgentResponse(BaseModel):
    id: str                      # same as request id
    agent: dict                  # { name, status }
    reply: dict                  # { text, type, channel, thread_ts }
    meta: dict = Field(default_factory=dict)

class ToolCall(BaseModel):
    id: str
    name: str
    args: dict
    requested_by: str            # usually the LLM

class ToolResult(BaseModel):
    id: str
    success: bool
    output: str
    metadata: dict = Field(default_factory=dict)

class LLMRequest(BaseModel):
    prompt: str
    context: ContextBundle
    temperature: float = 0.7
    max_tokens: int = 1024

class LLMResponse(BaseModel):
    text: str
    tokens_used: int
    finish_reason: str
    tool_calls: List[ToolCall] = Field(default_factory=list)