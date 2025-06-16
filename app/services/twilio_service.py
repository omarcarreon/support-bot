from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.core.config import settings
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER

    async def make_call(self, to_number: str, url: str) -> Dict[str, Any]:
        """
        Initiate a phone call using Twilio.
        
        Args:
            to_number: The phone number to call
            url: The webhook URL for TwiML instructions
            
        Returns:
            Dict containing call details
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=url
            )
            logger.info(f"Call initiated to {to_number} with SID: {call.sid}")
            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction
            }
        except Exception as e:
            logger.error(f"Error making call: {str(e)}")
            raise

    def generate_twiml(self, text: str, gather_input: bool = True) -> str:
        """
        Generate TwiML for voice response.
        
        Args:
            text: The text to be spoken
            gather_input: Whether to gather user input after speaking
            
        Returns:
            TwiML string
        """
        response = VoiceResponse()
        
        # Add text-to-speech
        response.say(text, voice="Polly.Lupe", language="es-MX")
        
        # If we want to gather input
        if gather_input:
            gather = Gather(
                input='speech',
                language='es-MX',
                speech_timeout='auto',
                action='/api/v1/voice/response',
                method='POST'
            )
            response.append(gather)
            
            # If no input is received, repeat the prompt
            response.redirect('/api/v1/voice/response')
        
        return str(response)

    def validate_twilio_request(self, signature: str, url: str, params: Dict[str, Any]) -> bool:
        """
        Validate that the request is coming from Twilio.
        
        Args:
            signature: The X-Twilio-Signature header
            url: The full URL of the request
            params: The POST parameters
            
        Returns:
            bool indicating if the request is valid
        """
        try:
            return self.client.validate_request(
                settings.TWILIO_AUTH_TOKEN,
                signature,
                url,
                params
            )
        except Exception as e:
            logger.error(f"Error validating Twilio request: {str(e)}")
            return False 