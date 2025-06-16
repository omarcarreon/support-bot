import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from chromadb import Client, Settings
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_collections():
    logger.info(f"Connecting to ChromaDB at: {settings.CHROMA_PERSIST_DIR}")
    client = Client(Settings(
        persist_directory=settings.CHROMA_PERSIST_DIR,
        anonymized_telemetry=False,
        is_persistent=True
    ))
    collections = client.list_collections()
    logger.info(f"Found {len(collections)} collections.")
    for collection in collections:
        logger.info(f"Deleting collection: {collection.name}")
        client.delete_collection(collection.name)
    logger.info("All collections deleted.")

if __name__ == "__main__":
    clean_collections() 