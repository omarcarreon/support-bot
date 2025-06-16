import sys
from pathlib import Path
import os
import logging
import json

# Add the app directory to Python path
app_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(app_dir)

from chromadb import Client, Settings
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_collection_info(collection):
    """Print information about a collection."""
    print(f"\nCollection: {collection.name}")
    print(f"Count: {collection.count()}")
    
    # Get all items
    results = collection.get()
    
    if results and results['ids']:
        print("\nSample Documents:")
        for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
            print(f"\nDocument {i+1}:")
            print(f"ID: {results['ids'][i]}")
            print(f"Content: {doc[:200]}...")  # First 200 chars
            print(f"Metadata: {json.dumps(metadata, indent=2)}")
            if i == 2:  # Show up to 3 samples
                break
    else:
        print("No documents found in collection")

def main():
    # Print debug information
    print(f"ChromaDB persist directory: {settings.CHROMA_PERSIST_DIR}")
    print(f"Directory exists: {os.path.exists(settings.CHROMA_PERSIST_DIR)}")
    if os.path.exists(settings.CHROMA_PERSIST_DIR):
        print(f"Directory contents: {os.listdir(settings.CHROMA_PERSIST_DIR)}")
        print(f"Directory permissions: {oct(os.stat(settings.CHROMA_PERSIST_DIR).st_mode)[-3:]}")
    
    try:
        # Initialize ChromaDB client
        logger.info("Initializing ChromaDB client...")
        client = Client(Settings(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False,
            is_persistent=True
        ))
        logger.info("ChromaDB client initialized successfully")
        
        # List all collections
        logger.info("Listing collections...")
        collections = client.list_collections()
        print(f"\nFound {len(collections)} collections:")
        
        for collection in collections:
            print(f"- {collection.name}")
            logger.info(f"Found collection: {collection.name}")
        
        # Print detailed info for each collection
        for collection in collections:
            print_collection_info(collection)
            
    except Exception as e:
        logger.error(f"Error accessing ChromaDB: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 