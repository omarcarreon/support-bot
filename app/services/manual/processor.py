import os
import re
import logging
import tempfile
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import json
import asyncio
from fastapi import UploadFile
import PyPDF2
from app.core.config import settings
from app.core.chunking.text_splitter import ManualTextSplitter
from app.core.embeddings.manager import EmbeddingsManager
from app.core.storage import ChromaStorage

logger = logging.getLogger(__name__)

class ManualProcessor:
    def __init__(self, tenant_id: str):
        """
        Initialize the manual processor.
        
        Args:
            tenant_id: The ID of the tenant
        """
        self.tenant_id = tenant_id
        self.text_splitter = ManualTextSplitter()
        self.embeddings_manager = EmbeddingsManager()
        self.storage = ChromaStorage(tenant_id)
        
        # Create temp directory if it doesn't exist
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create data directory if it doesn't exist
        self.data_dir = Path(settings.DATA_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def process_manual(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process a manual PDF file.
        
        Args:
            file: The uploaded PDF file
            
        Returns:
            Dict containing processing results
        """
        try:
            # Save the uploaded file
            temp_path = await self._save_uploaded_file(file)
            logger.info(f"Saved uploaded file to {temp_path}")
            
            # Extract text from PDF
            text = self._extract_text_from_pdf(temp_path)
            if not text:
                raise ValueError("No text could be extracted from the PDF")
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            
            # Split text into chunks
            documents = self.text_splitter.split_text(text, filename=file.filename)
            logger.info(f"Split text into {len(documents)} chunks")
            
            # Generate embeddings
            embeddings = await self.embeddings_manager.generate_embeddings([doc.page_content for doc in documents])
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Store in ChromaDB
            await self.storage.store_documents(documents, embeddings)
            logger.info("Stored documents in ChromaDB")
            
            # Clean up temp file
            os.remove(temp_path)
            logger.info(f"Removed temp file {temp_path}")
            
            return {
                "status": "completed",
                "total_chunks": len(documents),
                "processed_chunks": len(documents),
                "message": "Manual processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing manual: {str(e)}")
            raise

    async def _save_uploaded_file(self, file: UploadFile) -> str:
        """
        Save an uploaded file to a temporary location.
        
        Args:
            file: The uploaded file
            
        Returns:
            Path to the saved file
        """
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=self.temp_dir)
            temp_path = temp_file.name
            
            # Write the uploaded file to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}")
            raise

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using PyPDF2.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        logger.info("Extracting text using PyPDF2")
        text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                logger.info(f"PDF has {total_pages} pages")
                
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            # Add page marker
                            text += f"\n\n--- Page {i+1} ---\n\n{page_text}"
                            logger.info(f"Extracted text from page {i+1}")
                        else:
                            logger.warning(f"No text extracted from page {i+1}")
                            
                    except Exception as e:
                        logger.error(f"Error processing page {i+1}: {str(e)}")
                    
                    if (i + 1) % 10 == 0:  # Log every 10 pages
                        logger.info(f"Processed {i + 1} pages")
                
                logger.info(f"Total extracted text length: {len(text)} characters")
                return text
                
        except Exception as e:
            logger.error(f"Error in PDF processing: {str(e)}")
            raise 

    async def semantic_search(
        self,
        tenant_id: str,
        query: str,
        n_results: int = 3,
        relevance_threshold: float = 0.3,
        context_window_size: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search with context windows and advanced scoring.
        
        Args:
            tenant_id: The tenant ID
            query: The search query
            n_results: Number of results to return
            relevance_threshold: Minimum relevance score threshold
            context_window_size: Number of chunks to include before/after each result
            
        Returns:
            List of search results with enhanced context and scoring
        """
        try:
            logger.info(f"Performing semantic search for query: {query}")
            logger.info(f"Parameters: n_results={n_results}, threshold={relevance_threshold}, context_window={context_window_size}")
            
            # Generate query embedding
            query_embedding = await self.embeddings_manager.generate_embeddings([query])
            if not query_embedding:
                raise ValueError("Failed to generate query embedding")
            
            # Get initial results with more candidates for filtering
            initial_results = await self.storage.query_documents(
                query_embedding=query_embedding[0],
                n_results=n_results * 3  # Get more results for better filtering
            )
            
            logger.info(f"Retrieved {len(initial_results)} initial results")
            
            # Filter by relevance threshold
            filtered_results = [
                result for result in initial_results 
                if result['score'] >= relevance_threshold
            ]
            
            logger.info(f"After relevance filtering: {len(filtered_results)} results")
            
            if not filtered_results:
                logger.warning("No results passed relevance threshold")
                return []
            
            # Expand context windows for each result
            enhanced_results = []
            for i, result in enumerate(filtered_results[:n_results]):
                try:
                    enhanced_result = await self._expand_context_window(
                        result, context_window_size
                    )
                    enhanced_result['rank'] = i + 1
                    enhanced_results.append(enhanced_result)
                except Exception as e:
                    logger.error(f"Error expanding context for result {i}: {str(e)}")
                    # Fallback to original result
                    result['rank'] = i + 1
                    result['metadata']['context_size'] = 1
                    result['metadata']['original_score'] = result['score']
                    result['metadata']['context_coherence'] = 1.0
                    result['metadata']['position_score'] = 1.0
                    enhanced_results.append(result)
            
            # Sort by final score (descending)
            enhanced_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Update ranks after sorting
            for i, result in enumerate(enhanced_results):
                result['rank'] = i + 1
            
            logger.info(f"Returning {len(enhanced_results)} enhanced results")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}", exc_info=True)
            raise

    async def _expand_context_window(
        self, 
        result: Dict[str, Any], 
        context_window_size: int
    ) -> Dict[str, Any]:
        """
        Expand the context window around a search result.
        
        Args:
            result: The original search result
            context_window_size: Number of chunks to include before/after
            
        Returns:
            Enhanced result with expanded context
        """
        try:
            chunk_number = result['metadata'].get('chunk_number', 0)
            original_score = result['score']
            
            # Get surrounding chunks
            context_chunks = []
            context_scores = []
            
            # Get chunks before and after
            start_chunk = max(0, chunk_number - context_window_size)
            end_chunk = chunk_number + context_window_size + 1
            
            for chunk_idx in range(start_chunk, end_chunk):
                if chunk_idx == chunk_number:
                    # This is the original chunk
                    context_chunks.append(result['text'])
                    context_scores.append(original_score)
                else:
                    # Try to get adjacent chunk
                    try:
                        chunk_result = await self._get_chunk_by_number(chunk_idx)
                        if chunk_result:
                            context_chunks.append(chunk_result['text'])
                            context_scores.append(chunk_result.get('score', 0.1))
                        else:
                            # If chunk doesn't exist, add placeholder
                            context_chunks.append("")
                            context_scores.append(0.0)
                    except Exception as e:
                        logger.warning(f"Could not retrieve chunk {chunk_idx}: {str(e)}")
                        context_chunks.append("")
                        context_scores.append(0.0)
            
            # Remove empty chunks
            valid_chunks = [(chunk, score) for chunk, score in zip(context_chunks, context_scores) if chunk.strip()]
            
            if not valid_chunks:
                # Fallback to original result
                logger.warning("No valid context chunks found, using original")
                result['metadata']['context_size'] = 1
                result['metadata']['original_score'] = original_score
                result['metadata']['context_coherence'] = 1.0
                result['metadata']['position_score'] = 1.0
                return result
            
            # Combine context chunks
            combined_text = "\n\n".join([chunk for chunk, _ in valid_chunks])
            
            # Calculate context coherence (average of non-zero scores)
            non_zero_scores = [score for _, score in valid_chunks if score > 0]
            context_coherence = sum(non_zero_scores) / len(non_zero_scores) if non_zero_scores else 0.1
            
            # Calculate position score (higher for chunks in the middle of context)
            total_chunks = len(valid_chunks)
            original_position = next(
                (i for i, (chunk, score) in enumerate(valid_chunks) if score == original_score),
                total_chunks // 2
            )
            
            # Position score is higher when the original chunk is in the center
            if total_chunks == 1:
                position_score = 1.0
            else:
                # Score from 0.5 to 1.0 based on how centered the original chunk is
                center_distance = abs(original_position - (total_chunks - 1) / 2)
                max_distance = (total_chunks - 1) / 2
                position_score = 0.5 + 0.5 * (1 - center_distance / max_distance)
            
            # Calculate final score (weighted combination)
            final_score = (
                0.6 * original_score +           # Original relevance (60%)
                0.3 * context_coherence +        # Context coherence (30%)
                0.1 * position_score             # Position bonus (10%)
            )
            
            # Create enhanced result
            enhanced_result = {
                'text': combined_text,
                'score': final_score,
                'metadata': {
                    **result['metadata'],
                    'original_score': original_score,
                    'context_coherence': context_coherence,
                    'position_score': position_score,
                    'context_size': len(valid_chunks)
                }
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error expanding context window: {str(e)}")
            # Return original result as fallback
            result['metadata']['context_size'] = 1
            result['metadata']['original_score'] = result['score']
            result['metadata']['context_coherence'] = 1.0
            result['metadata']['position_score'] = 1.0
            return result

    async def _get_chunk_by_number(self, chunk_number: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific chunk by its number.
        
        Args:
            chunk_number: The chunk number to retrieve
            
        Returns:
            The chunk data if found, None otherwise
        """
        try:
            # Query ChromaDB for the specific chunk
            # This is a simplified implementation - in practice, you might want to
            # implement a more efficient chunk retrieval method
            results = await self.storage.query_documents(
                query_embedding=[0.0] * 1536,  # Dummy embedding
                n_results=1000  # Get many results to find the specific chunk
            )
            
            # Find the chunk with the matching chunk number
            for result in results:
                if result['metadata'].get('chunk_number') == chunk_number:
                    return result
            
            return None
            
        except Exception as e:
            logger.warning(f"Error retrieving chunk {chunk_number}: {str(e)}")
            return None 