from typing import Optional
import logging
import os
from pathlib import Path
import asyncio
from app.core.config import settings
import aiohttp
import json

logger = logging.getLogger(__name__)

class SpeechService:
    """Service for handling speech-to-text conversion."""
    
    def __init__(self):
        """Initialize speech service with OpenAI API key."""
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    async def transcribe_audio(
        self,
        audio_path: str,
        language: str = "es"
    ) -> Optional[str]:
        """
        Transcribe audio file to text using OpenAI's Whisper API.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (default: "es" for Spanish)
            
        Returns:
            Optional[str]: Transcribed text or None if transcription fails
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = aiohttp.FormData()
        data.add_field('file',
                      open(audio_path, 'rb'),
                      filename=os.path.basename(audio_path))
        data.add_field('model', 'whisper-1')
        data.add_field('language', language)
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.api_url,
                        headers=headers,
                        data=data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result.get('text')
                        else:
                            error_text = await response.text()
                            logger.error(f"Transcription failed (attempt {attempt + 1}/{self.max_retries}): {error_text}")
                            
            except Exception as e:
                logger.error(f"Error during transcription (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                
        return None 