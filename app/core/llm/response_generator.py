from typing import Dict, Any, List, Optional
import logging
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from app.core.config import settings
from app.core.chroma import chroma_client
from app.schemas.ask import ConversationMessage

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generates responses using LangChain and GPT."""
    
    _embeddings = None
    _llm = None
    
    @classmethod
    def _get_embeddings(cls):
        """Get or create embeddings instance."""
        if cls._embeddings is None:
            cls._embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=settings.OPENAI_API_KEY,
                model_kwargs={}  # Empty dict to avoid any proxy-related issues
            )
            logger.info("Initialized OpenAI embeddings with text-embedding-3-small model")
        return cls._embeddings
    
    @classmethod
    def _get_llm(cls):
        """Get or create LLM instance."""
        if cls._llm is None:
            cls._llm = ChatOpenAI(
                model_name="gpt-4",
                temperature=0.7,
                streaming=True
            )
        return cls._llm
    
    def __init__(self, collection_name: str):
        """Initialize the response generator.
        
        Args:
            collection_name: Name of the ChromaDB collection to use
        """
        # Ensure collection name has the correct format
        if not collection_name.startswith('tenant_'):
            collection_name = f"tenant_{collection_name}"
        self.collection_name = collection_name
        logger.info(f"Initializing ResponseGenerator with collection: {self.collection_name}")
        
        self.embeddings = self._get_embeddings()
        self.llm = self._get_llm()
        self.qa_chain = self._create_qa_chain()
        
    def _create_qa_chain(self) -> RetrievalQA:
        """Create the QA chain for response generation."""
        # Initialize vector store using singleton client
        vectorstore = Chroma(
            client=chroma_client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
        
        # Create prompt template
        template = """You are a helpful technical support assistant. Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create the chain
        chain = (
            {"context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
            | prompt
            | self.llm
        )
        
        return chain
    
    async def generate_response(
        self,
        question: str,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[ConversationMessage]] = None
    ) -> Dict[str, Any]:
        """Generate a response for the given question.
        
        Args:
            question: The question to answer
            conversation_id: Optional ID for conversation tracking
            conversation_history: Optional list of previous conversation messages
            
        Returns:
            Dict containing the answer and metadata
        """
        try:
            # Get source documents using the vectorstore directly
            vectorstore = Chroma(
                client=chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
            # Log collection info
            logger.info(f"Querying collection: {self.collection_name}")
            collection = chroma_client.get_collection(self.collection_name)
            collection_count = collection.count()
            logger.info(f"Collection has {collection_count} documents")
            
            if collection_count == 0:
                logger.warning("No documents found in collection")
                return {
                    "answer": "Lo siento, no tengo suficiente contexto para responder a esta pregunta. Por favor, asegúrese de que el manual haya sido cargado correctamente.",
                    "sources": [],
                    "confidence": 0.0,
                    "conversation_id": conversation_id,
                    "conversation_history": conversation_history or []
                }
            
            # Get relevant documents
            logger.info("Generating embeddings for question and searching similar documents...")
            docs = await vectorstore.asimilarity_search(question, k=3)
            logger.info(f"Found {len(docs)} relevant documents")
            
            if not docs:
                logger.warning("No relevant documents found for question")
                return {
                    "answer": "Lo siento, no pude encontrar información relevante en el manual para responder a esta pregunta.",
                    "sources": [],
                    "confidence": 0.0,
                    "conversation_id": conversation_id,
                    "conversation_history": conversation_history or []
                }
            
            # Get response from chain with context
            logger.info("Generating response using QA chain...")
            response = await self.qa_chain.ainvoke(question)
            logger.info("Response generated successfully")
            
            # Calculate confidence based on number of relevant sources
            confidence = min(len(docs) / 3, 1.0)  # Cap at 1.0
            
            # Create updated conversation history
            updated_history = conversation_history or []
            updated_history.extend([
                ConversationMessage(role="user", content=question),
                ConversationMessage(role="assistant", content=response.content)
            ])
            
            # Format source documents
            sources = []
            for doc in docs:
                metadata = doc.metadata
                source = {
                    "page": metadata.get("page", 0),
                    "section": metadata.get("section", ""),
                    "filename": metadata.get("filename", "")
                }
                # Only add non-empty sources
                if any(source.values()):
                    sources.append(source)
            
            return {
                "answer": response.content,
                "sources": sources,
                "confidence": confidence,
                "conversation_id": conversation_id,
                "conversation_history": updated_history
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise 