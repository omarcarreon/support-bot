import os
import logging
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_data_directory():
    """Initialize the data directory for ChromaDB."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        logger.info(f"Created data directory: {settings.CHROMA_PERSIST_DIR}")
        
        # Set permissions (readable and writable by all)
        os.chmod(settings.CHROMA_PERSIST_DIR, 0o777)
        logger.info(f"Set permissions on data directory")
        
        # List contents
        contents = os.listdir(settings.CHROMA_PERSIST_DIR)
        logger.info(f"Data directory contents: {contents}")
        
    except Exception as e:
        logger.error(f"Error initializing data directory: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    init_data_directory() 