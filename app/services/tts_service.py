from typing import Optional, Dict, Any
import logging
import os
from pathlib import Path
import asyncio
from app.core.config import settings
import aiohttp
import json
import aiofiles
from datetime import datetime

logger = logging.getLogger(__name__)

class TTSService:
    """Service for handling text-to-speech conversion."""
    
    def __init__(self):
        """Initialize TTS service with OpenAI API key."""
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/audio/speech"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Voice settings
        self.voice = "alloy"  # OpenAI's default voice
        self.model = "tts-1"  # OpenAI's default model
        self.speed = 1.0  # Normal speed
        
    async def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None
    ) -> Optional[str]:
        """
        Convert text to speech using OpenAI's TTS API.
        
        Args:
            text: The text to convert to speech
            voice: Voice to use (optional, defaults to self.voice)
            speed: Speech speed (optional, defaults to self.speed)
            
        Returns:
            Optional[str]: Path to the generated audio file or None if conversion fails
        """
        if not text:
            logger.error("Empty text provided for TTS conversion")
            return None
            
        # Use provided voice/speed or defaults
        voice = voice or self.voice
        speed = speed or self.speed
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": text,
            "voice": voice,
            "speed": speed
        }
        
        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.temp_dir / f"tts_{timestamp}.mp3"
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.api_url,
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status == 200:
                            # Save the audio file
                            async with aiofiles.open(output_path, 'wb') as f:
                                await f.write(await response.read())
                            return str(output_path)
                        else:
                            error_text = await response.text()
                            logger.error(f"TTS conversion failed (attempt {attempt + 1}/{self.max_retries}): {error_text}")
                            
            except Exception as e:
                logger.error(f"Error during TTS conversion (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                
        return None
        
    async def cleanup_audio_file(self, file_path: str) -> None:
        """
        Clean up temporary audio file.
        
        Args:
            file_path: Path to the audio file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up audio file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up audio file {file_path}: {str(e)}")
            
    def generate_ssml(self, text: str, voice: Optional[str] = None, speed: Optional[float] = None) -> str:
        """
        Generate SSML markup for text.
        
        Args:
            text: The text to convert to SSML
            voice: Voice to use (optional)
            speed: Speech speed (optional)
            
        Returns:
            str: SSML markup
        """
        voice = voice or self.voice
        speed = speed or self.speed
        
        # Basic SSML with voice and speed settings
        ssml = f"""
        <speak>
            <voice name="{voice}">
                <prosody rate="{speed}">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        return ssml.strip() 