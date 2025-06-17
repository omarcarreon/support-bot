from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from app.core.cache import Cache
from app.schemas.ask import ConversationMessage

logger = logging.getLogger(__name__)

class ConversationStorage:
    """Service for managing conversation storage and retrieval."""
    
    def __init__(self, cache: Cache):
        """Initialize with cache instance."""
        self.cache = cache
        self.conversation_ttl = 24 * 3600  # 24 hours in seconds
        
    async def store_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
        messages: List[ConversationMessage]
    ) -> None:
        """Store conversation messages in cache."""
        try:
            cache_key = f"conversation:{tenant_id}:{conversation_id}"
            await self.cache.set(
                cache_key,
                [msg.dict() for msg in messages],
                expire=self.conversation_ttl,
                tags=[f"tenant:{tenant_id}", f"conversation:{conversation_id}"]
            )
            logger.info(f"Stored conversation {conversation_id} for tenant {tenant_id}")
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")
            raise
            
    async def get_conversation(
        self,
        tenant_id: str,
        conversation_id: str
    ) -> Optional[List[ConversationMessage]]:
        """Retrieve conversation messages from cache."""
        try:
            cache_key = f"conversation:{tenant_id}:{conversation_id}"
            messages_data = await self.cache.get(cache_key)
            
            if not messages_data:
                logger.info(f"No conversation found for {conversation_id}")
                return None
                
            return [ConversationMessage(**msg) for msg in messages_data]
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            return None
            
    async def add_message(
        self,
        tenant_id: str,
        conversation_id: str,
        message: ConversationMessage
    ) -> None:
        """Add a single message to an existing conversation."""
        try:
            # Get existing conversation
            messages = await self.get_conversation(tenant_id, conversation_id) or []
            
            # Add new message
            messages.append(message)
            
            # Store updated conversation
            await self.store_conversation(tenant_id, conversation_id, messages)
            logger.info(f"Added message to conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error adding message to conversation: {str(e)}")
            raise
            
    async def cleanup_expired_conversations(self) -> None:
        """Clean up expired conversations."""
        try:
            # The cache will automatically handle expiration
            # This method is for explicit cleanup if needed
            logger.info("Running conversation cleanup")
            # Add any specific cleanup logic here if needed
        except Exception as e:
            logger.error(f"Error cleaning up conversations: {str(e)}")
            raise 