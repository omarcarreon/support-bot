from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class MessageType(str, Enum):
    """Types of WhatsApp messages."""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    DOCUMENT = "document"

class MessageStatus(str, Enum):
    """Status of WhatsApp messages."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class MessageResponse(BaseModel):
    """Response model for WhatsApp messages."""
    message_id: str
    status: MessageStatus
    timestamp: datetime
    type: MessageType
    recipient_id: str
    conversation_id: Optional[str] = None
    error: Optional[str] = None

class StatusUpdate(BaseModel):
    """Model for WhatsApp status updates."""
    id: str
    status: MessageStatus
    timestamp: datetime
    recipient_id: str
    conversation_id: Optional[str] = None 