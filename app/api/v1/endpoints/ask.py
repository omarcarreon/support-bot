from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ask import AskRequest, AskResponse, SourceDocument, ConversationMessage
from app.core.llm.response_generator import ResponseGenerator
from app.core.middleware import get_tenant_id
from app.core.cache import get_cache, Cache
from app.services.conversation.storage import ConversationStorage
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=AskResponse)
async def ask(
    request: AskRequest,
    tenant_id: str = Depends(get_tenant_id),
    cache: Cache = Depends(get_cache)
) -> AskResponse:
    """
    Process a question and generate a response based on the tenant's manual.
    
    Args:
        request: The question request containing the operator's question
        tenant_id: The current tenant ID (injected)
        cache: Cache instance (injected)
        
    Returns:
        AskResponse containing the generated answer and metadata
    """
    try:
        logger.info(f"Processing question for tenant {tenant_id}: {request.question[:100]}...")
        
        # Initialize conversation storage
        conversation_storage = ConversationStorage(cache)
        
        # Generate or use conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        logger.debug(f"Using conversation ID: {conversation_id}")
        
        # Get existing conversation history
        conversation_history = await conversation_storage.get_conversation(
            tenant_id,
            conversation_id
        ) or request.conversation_history or []
        
        # Check cache first
        cache_key = f"ask:{tenant_id}:{conversation_id}:{request.question}"
        logger.debug(f"Checking cache with key: {cache_key}")
        cached_response = await cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for question: {request.question[:100]}...")
            return AskResponse(**cached_response)
        logger.debug("Cache miss, proceeding with response generation")
        
        # Initialize response generator for tenant's collection
        logger.info(f"Initializing ResponseGenerator for tenant {tenant_id}")
        response_generator = ResponseGenerator(collection_name=tenant_id)
        
        # Generate response
        logger.info("Generating response...")
        response = await response_generator.generate_response(
            question=request.question,
            conversation_id=conversation_id,
            conversation_history=conversation_history
        )
        logger.info("Response generated successfully")
        
        # Convert source documents to our schema
        sources = [
            SourceDocument(
                page=doc.get("page"),
                section=doc.get("section"),
                filename=doc.get("filename")
            )
            for doc in response["sources"]
        ]
        logger.debug(f"Found {len(sources)} source documents")
        
        # Create response object
        ask_response = AskResponse(
            answer=response["answer"],
            sources=sources,
            confidence=response["confidence"],
            conversation_id=response["conversation_id"],
            conversation_history=response["conversation_history"]
        )
        
        # Store updated conversation history
        await conversation_storage.store_conversation(
            tenant_id,
            conversation_id,
            ask_response.conversation_history
        )
        
        # Cache the response with tags for invalidation
        logger.debug("Caching response...")
        tags = [
            f"tenant:{tenant_id}",
            f"conversation:{response['conversation_id']}" if response['conversation_id'] else None
        ]
        # Filter out None values from tags
        tags = [tag for tag in tags if tag is not None]
        await cache.set(
            cache_key,
            ask_response.dict(),
            expire=Cache.DEFAULT_TTL,  # Use default TTL
            tags=tags
        )
        logger.info("Response cached successfully")
        
        # Log cache statistics
        stats = cache.get_stats()
        logger.info(f"Cache stats - Hits: {stats['hits']}, Misses: {stats['misses']}, Sets: {stats['sets']}")
        
        return ask_response
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error processing your question. Please try again."
        ) 