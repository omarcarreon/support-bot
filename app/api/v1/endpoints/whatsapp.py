from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks, Query
from app.services.whatsapp_service import WhatsAppService
from app.core.config import get_settings
from app.api.v1.endpoints.ask import ask
from app.core.middleware import get_tenant_id
from app.schemas.ask import AskRequest
from app.core.cache import get_cache
import logging
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)

# Hardcoded mapping for testing - replace with your actual values
WHATSAPP_TO_TENANT = {
    "5218112302225": "2f510469-f2ff-49d5-9466-24df4435de20"  # Replace with your test number and tenant UUID
}

@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks, cache = Depends(get_cache)):
    """Handle incoming WhatsApp Cloud API messages."""
    try:
        # Initialize WhatsApp service
        whatsapp_service = WhatsAppService(cache=cache)
        
        body = await request.json()
        logger.info(f"Received webhook body: {body}")

        # Handle status updates
        if "entry" in body and body["entry"]:
            for entry in body["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("value", {}).get("statuses"):
                            # Handle status updates
                            for status in change["value"]["statuses"]:
                                await whatsapp_service.handle_status_update(status)
                            continue

        # Extract messages from the nested structure
        messages = []
        if "entry" in body and body["entry"]:
            for entry in body["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if "value" in change and "messages" in change["value"]:
                            messages.extend(change["value"]["messages"])

        if not messages:
            logger.info("No messages in body")
            return {"status": "ok"}

        logger.info(f"Processing {len(messages)} messages")
        
        # Process each message
        for message in messages:
            if message.get("type") == "text":
                # Get the sender's phone number
                from_number = message.get("from")
                
                # Get tenant ID from mapping
                tenant_id = WHATSAPP_TO_TENANT.get(from_number)
                if not tenant_id:
                    logger.warning(f"No tenant mapping found for number: {from_number}")
                    await whatsapp_service.send_text_message(
                        to_number=from_number,
                        text="Sorry, this number is not registered with our service."
                    )
                    continue

                # Get the text content
                text_content = message.get("text", {}).get("body", "")
                logger.info(f"Processing text message from {from_number}: {text_content}")

                # Create AskRequest object
                ask_request = AskRequest(
                    question=text_content,
                    conversation_id=message.get("conversation", {}).get("id")
                )

                # Call the ask endpoint with the tenant ID and cache
                response = await ask(
                    request=ask_request,
                    tenant_id=tenant_id,
                    cache=cache
                )

                # Send the response back via WhatsApp
                await whatsapp_service.send_text_message(
                    to_number=from_number,
                    text=response.answer
                )
            else:
                # For non-text messages, send a message asking for text
                from_number = message.get("from")
                await whatsapp_service.send_text_message(
                    to_number=from_number,
                    text="Please send your question as a text message."
                )

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    """Verify the webhook for WhatsApp Cloud API."""
    settings = get_settings()
    logger.info(f"Webhook verification attempt - mode: {hub_mode}, token: {hub_verify_token}, challenge: {hub_challenge}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verification successful")
        return hub_challenge
    else:
        logger.warning(f"Webhook verification failed - expected token: {settings.WHATSAPP_VERIFY_TOKEN}")
        raise HTTPException(status_code=403, detail="Verification failed") 