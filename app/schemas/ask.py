from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ConversationMessage(BaseModel):
    """Model for a single message in a conversation."""
    role: MessageRole
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the message was sent")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AskRequest(BaseModel):
    """Request model for the /ask endpoint."""
    question: str = Field(..., min_length=1, max_length=500, description="The question to ask about the manual")
    conversation_id: Optional[str] = Field(None, description="Optional ID for conversation tracking")
    conversation_history: Optional[List[ConversationMessage]] = Field(default_factory=list, description="Previous messages in the conversation")

class SourceDocument(BaseModel):
    """Model for a source document used in generating the response."""
    page: Optional[int] = Field(None, description="Page number in the source document")
    section: Optional[str] = Field(None, description="Section name in the source document")
    filename: Optional[str] = Field(None, description="Name of the source file")

class AskResponse(BaseModel):
    """Response model for the /ask endpoint."""
    answer: str = Field(..., description="The answer to the question")
    sources: List[SourceDocument] = Field(default_factory=list, description="List of sources used to generate the answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")
    conversation_history: List[ConversationMessage] = Field(default_factory=list, description="Updated conversation history including this response")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 