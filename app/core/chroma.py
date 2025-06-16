from chromadb import Client, Settings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChromaClient:
    """Singleton ChromaDB client."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> Client:
        """Get or create the ChromaDB client instance."""
        if cls._instance is None:
            logger.info("Initializing ChromaDB client...")
            cls._instance = Client(Settings(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                anonymized_telemetry=False,
                is_persistent=True
            ))
            logger.info("ChromaDB client initialized successfully")
        return cls._instance

# Create a global instance
chroma_client = ChromaClient.get_instance() 