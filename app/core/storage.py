import os
import logging
from typing import List, Dict, Any
from chromadb import Client, Settings
from langchain.schema import Document
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChromaStorage:
    def __init__(self, tenant_id: str):
        """
        Initialize ChromaDB storage for a specific tenant.
        
        Args:
            tenant_id: The ID of the tenant
        """
        self.tenant_id = tenant_id
        self.collection_name = f"tenant_{tenant_id}"
        
        # Initialize ChromaDB client
        self.client = Client(Settings(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False,
            is_persistent=True
        ))
        
        # Get or create collection
        try:
            # Try to get existing collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"Retrieved existing collection: {self.collection_name}")
            except Exception as e:
                # Collection doesn't exist, create it
                logger.info(f"Collection {self.collection_name} not found, creating new one")
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"tenant_id": tenant_id}
                )
                logger.info(f"Created new collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collection: {str(e)}")
            raise

    async def store_documents(self, documents: List[Document], embeddings: List[List[float]]) -> None:
        """
        Store documents and their embeddings in ChromaDB.
        
        Args:
            documents: List of Document objects
            embeddings: List of embedding vectors
        """
        try:
            # Prepare documents for storage
            documents_to_store = [doc.page_content for doc in documents]
            metadatas_to_store = []
            
            for i, doc in enumerate(documents):
                # Ensure all metadata values are of the correct type
                metadata = {
                    "tenant_id": str(self.tenant_id),
                    "chunk_number": int(i),
                    "page": int(doc.metadata.get("page", 0)),
                    "section": str(doc.metadata.get("section", "")),
                    "filename": str(doc.metadata.get("filename", "")),
                    "source": str(doc.metadata.get("source", ""))
                }
                metadatas_to_store.append(metadata)
            
            ids_to_store = [f"{self.tenant_id}_{i}" for i in range(len(documents))]

            # Add documents to collection
            self.collection.add(
                documents=documents_to_store,
                embeddings=embeddings,
                metadatas=metadatas_to_store,
                ids=ids_to_store
            )
            logger.info(f"Added {len(documents_to_store)} documents to collection")

            # Verify storage
            collection_count = self.collection.count()
            logger.info(f"Collection count after storage: {collection_count}")
            
            if collection_count != len(documents):
                raise ValueError(f"Document count mismatch! Expected {len(documents)}, got {collection_count}")

        except Exception as e:
            logger.error(f"Error storing documents in ChromaDB: {str(e)}")
            raise

    async def query_documents(self, query_embedding: List[float], n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query documents using an embedding vector.
        
        Args:
            query_embedding: The query embedding vector
            n_results: Number of results to return
            
        Returns:
            List of dictionaries containing the results
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            processed_results = []
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                # Convert distance to similarity score
                similarity_score = 1.0 / (1.0 + distance)
                
                processed_results.append({
                    "text": doc,
                    "score": similarity_score,
                    "metadata": metadata
                })
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            raise 