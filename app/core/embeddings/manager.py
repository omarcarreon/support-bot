from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from app.core.config import settings

class EmbeddingsManager:
    def __init__(self):
        """
        Initialize the embeddings manager with OpenAI embeddings.
        """
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY,
            model_kwargs={}  # Empty dict to avoid any proxy-related issues
        )

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        return await self.embeddings.aembed_documents(texts)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector
        """
        return await self.embeddings.aembed_query(text)

    async def generate_document_embeddings(self, documents: List[Document]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            documents: List of Document objects to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        texts = [doc.page_content for doc in documents]
        return await self.generate_embeddings(texts) 