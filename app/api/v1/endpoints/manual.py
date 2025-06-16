import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict

from app.services.manual.processor import ManualProcessor
from app.core.validation.pdf_validator import PDFValidator
from app.core.middleware import get_tenant_id
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_manual(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_tenant_id)
) -> Dict:
    """
    Upload and process a PDF manual.
    
    Args:
        file: The PDF file to upload
        tenant_id: The tenant ID (from middleware)
        
    Returns:
        Dict containing processing status and information
    """
    logger.debug(f"Uploading manual for tenant: {tenant_id}")
    
    try:
        # Initialize processor with tenant_id
        processor = ManualProcessor(tenant_id=tenant_id)
        
        # Process the manual
        result = await processor.process_manual(file)
        
        return {
            "status": "success",
            "message": result["message"],
            "total_chunks": result["total_chunks"],
            "processed_chunks": result["processed_chunks"]
        }
        
    except Exception as e:
        logger.error(f"Error processing manual: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 