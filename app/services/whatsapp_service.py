from typing import Dict, Any, Optional, BinaryIO
import requests
import logging
import json
from app.core.config import get_settings
import aiohttp
import aiofiles
import os
from pathlib import Path
import hmac
import hashlib
import asyncio
from datetime import datetime
import magic  # for MIME type detection
from app.schemas.whatsapp import MessageStatus, MessageType, MessageResponse
from app.core.cache import Cache

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for handling WhatsApp Cloud API interactions."""
    
    def __init__(self, cache: Optional[Cache] = None):
        """Initialize WhatsApp client with credentials from settings."""
        settings = get_settings()
        self.api_version = "v17.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.verify_token = settings.WHATSAPP_VERIFY_TOKEN
        self.app_secret = settings.WHATSAPP_APP_SECRET
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        self.cache = cache
        
        # Message settings
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.message_ttl = 3600  # 1 hour
        
        logger.info("Initialized WhatsApp Cloud API client")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for WhatsApp API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def send_text_message(
        self,
        to_number: str,
        text: str,
        conversation_id: Optional[str] = None
    ) -> Optional[MessageResponse]:
        """
        Send a text message via WhatsApp Cloud API.
        
        Args:
            to_number: The recipient's phone number
            text: The message text
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            Optional[MessageResponse]: Message response if successful, None if failed
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        # Cloud API message structure
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        headers=self._get_headers(),
                        json=payload,
                        timeout=30
                    ) as response:
                        response_data = await response.json()
                        logger.info(f"Message send response: {response_data}")
                        
                        if response.status == 200:
                            message_id = response_data.get("messages", [{}])[0].get("id")
                            
                            if message_id:
                                # Store initial status
                                await self._store_message_status(
                                    message_id=message_id,
                                    status=MessageStatus.SENT,
                                    message_type=MessageType.TEXT,
                                    recipient_id=to_number,
                                    conversation_id=conversation_id
                                )
                                
                                return MessageResponse(
                                    message_id=message_id,
                                    status=MessageStatus.SENT,
                                    timestamp=datetime.utcnow(),
                                    type=MessageType.TEXT,
                                    recipient_id=to_number,
                                    conversation_id=conversation_id
                                )
                        else:
                            error_message = response_data.get("error", {}).get("message", "Unknown error")
                            logger.error(f"Failed to send message (attempt {attempt + 1}/{self.max_retries}): {error_message}")
                            
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay)
                            else:
                                return None
                                
            except Exception as e:
                logger.error(f"Error sending message (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    return None

    async def _store_message_status(
        self,
        message_id: str,
        status: MessageStatus,
        message_type: MessageType,
        recipient_id: str,
        conversation_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Store message status in cache."""
        if not self.cache:
            return
            
        message_data = MessageResponse(
            message_id=message_id,
            status=status,
            timestamp=datetime.utcnow(),
            type=message_type,
            recipient_id=recipient_id,
            conversation_id=conversation_id,
            error=error
        )
        
        await self.cache.set(
            f"message:{message_id}",
            message_data.json(),
            expire=self.message_ttl
        )
        
        if conversation_id:
            # Store message ID in conversation history
            await self.cache.sadd(
                f"conversation:{conversation_id}:messages",
                message_id
            )

    async def _get_message_status(self, message_id: str) -> Optional[MessageResponse]:
        """Get message status from cache."""
        if not self.cache:
            return None
            
        data = await self.cache.get(f"message:{message_id}")
        if data:
            return MessageResponse.parse_raw(data)
        return None

    async def handle_status_update(self, status_update: Dict[str, Any]) -> None:
        """Handle message status updates."""
        try:
            message_id = status_update.get("id")
            if not message_id:
                return
                
            status = status_update.get("status")
            if not status:
                return
                
            # Get existing message data
            message_data = await self._get_message_status(message_id)
            if not message_data:
                return
                
            # Update status
            message_data.status = MessageStatus(status)
            message_data.timestamp = datetime.utcnow()
            
            # Store updated status
            await self.cache.set(
                f"message:{message_id}",
                message_data.json(),
                expire=self.message_ttl
            )
            
        except Exception as e:
            logger.error(f"Error handling status update: {str(e)}") 