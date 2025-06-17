from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.services.twilio_service import TwilioService
from app.core.llm.response_generator import ResponseGenerator
from app.core.middleware import get_tenant_id
from app.core.cache import get_cache, Cache
from app.services.conversation.storage import ConversationStorage
from app.schemas.ask import ConversationMessage
import logging
from typing import Dict, Any
import uuid
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/call")
async def initiate_call(
    request: Request,
    to_number: str,
    tenant_id: str = Depends(get_tenant_id),
    cache: Cache = Depends(get_cache)
) -> Dict[str, Any]:
    """
    Initiate a phone call to the specified number.
    
    Args:
        request: The FastAPI request object
        to_number: The phone number to call
        tenant_id: The current tenant ID (injected)
        cache: Cache instance (injected)
        
    Returns:
        Dict containing call details
    """
    try:
        # Initialize conversation storage
        conversation_storage = ConversationStorage(cache)
        
        # Generate a unique conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Store conversation ID in cache
        await cache.set(
            f"call:{tenant_id}:{to_number}",
            conversation_id,
            expire=3600  # 1 hour
        )
        
        # Initialize Twilio service
        twilio_service = TwilioService()
        
        # Generate webhook URL for TwiML
        webhook_url = f"{request.base_url}api/v1/voice/response"
        
        # Make the call
        call_details = await twilio_service.make_call(to_number, webhook_url)
        
        # Store initial conversation message
        await conversation_storage.add_message(
            tenant_id,
            conversation_id,
            ConversationMessage(
                role="assistant",
                content="Iniciando llamada de soporte técnico.",
                timestamp=datetime.utcnow()
            )
        )
        
        return {
            "status": "success",
            "call_sid": call_details["call_sid"],
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error initiating call. Please try again."
        )

@router.post("/response")
async def handle_voice_response(
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    cache: Cache = Depends(get_cache)
) -> Response:
    """
    Handle voice responses and generate bot responses.
    
    Args:
        request: The FastAPI request object
        tenant_id: The current tenant ID (injected)
        cache: Cache instance (injected)
        
    Returns:
        TwiML response
    """
    try:
        # Initialize conversation storage
        conversation_storage = ConversationStorage(cache)
        
        # Get form data
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        speech_result = form_data.get("SpeechResult")
        
        # Validate Twilio request
        twilio_service = TwilioService()
        if not twilio_service.validate_twilio_request(
            request.headers.get("X-Twilio-Signature", ""),
            str(request.url),
            dict(form_data)
        ):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")
        
        # Get conversation ID from cache
        conversation_id = await cache.get(f"call:{tenant_id}:{call_sid}")
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            await cache.set(
                f"call:{tenant_id}:{call_sid}",
                conversation_id,
                expire=3600
            )
        
        # Store user's speech input
        await conversation_storage.add_message(
            tenant_id,
            conversation_id,
            ConversationMessage(
                role="user",
                content=speech_result,
                timestamp=datetime.utcnow()
            )
        )
        
        # Get conversation history
        conversation_history = await conversation_storage.get_conversation(
            tenant_id,
            conversation_id
        )
        
        # Initialize response generator
        response_generator = ResponseGenerator(collection_name=tenant_id)
        
        # Generate response
        response = await response_generator.generate_response(
            question=speech_result,
            conversation_id=conversation_id,
            conversation_history=conversation_history
        )
        
        # Store bot's response
        await conversation_storage.add_message(
            tenant_id,
            conversation_id,
            ConversationMessage(
                role="assistant",
                content=response["answer"],
                timestamp=datetime.utcnow()
            )
        )
        
        # Generate TwiML
        twiml = twilio_service.generate_twiml(response["answer"])
        
        return Response(
            content=twiml,
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error handling voice response: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing voice response. Please try again."
        ) 