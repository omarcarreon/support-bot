import asyncio
import sys
from pathlib import Path
import logging
import json

# Add the app directory to Python path
app_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(app_dir)

from app.services.manual.processor import ManualProcessor
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_semantic_search():
    """Test semantic search functionality with context windows."""
    logger.info("Starting semantic search test")
    
    try:
        # Initialize the processor
        processor = ManualProcessor(tenant_id="2f510469-f2ff-49d5-9466-24df4435de20")
        
        # Test queries with different relevance thresholds and context windows
        test_queries = [
            {
                "query": "El equipo Merrychef Eikon E2S no enciende",
                "tenant_id": "2f510469-f2ff-49d5-9466-24df4435de20",
                "n_results": 3,
                "relevance_threshold": 0.3,
                "context_window_size": 2
            },
        ]
        
        for test_case in test_queries:
            logger.info(f"\nTesting query: {test_case['query']}")
            logger.info(f"Parameters: n_results={test_case['n_results']}, "
                       f"threshold={test_case['relevance_threshold']}, "
                       f"context_window={test_case['context_window_size']}")
            
            results = await processor.semantic_search(
                tenant_id=test_case['tenant_id'],
                query=test_case['query'],
                n_results=test_case['n_results'],
                relevance_threshold=test_case['relevance_threshold'],
                context_window_size=test_case['context_window_size']
            )
            
            logger.info(f"Found {len(results)} results")
            
            # Print results in a readable format
            for result in results:
                logger.info(f"\nResult #{result['rank']}:")
                logger.info(f"Final Score: {result['score']:.3f}")
                logger.info(f"Original Score: {result['metadata']['original_score']:.3f}")
                logger.info(f"Context Coherence: {result['metadata']['context_coherence']:.3f}")
                logger.info(f"Position Score: {result['metadata']['position_score']:.3f}")
                logger.info(f"Context Size: {result['metadata']['context_size']} chunks")
                logger.info(f"Chunk Number: {result['metadata']['chunk_number']}")
                logger.info(f"Text: {result['text'][:500]}...")  # First 500 chars
                logger.info(f"Additional Metadata: {json.dumps({k:v for k,v in result['metadata'].items() if k not in ['original_score', 'context_coherence', 'position_score', 'context_size', 'chunk_number']}, indent=2)}")
            
            logger.info("-" * 80)
        
        logger.info("Semantic search test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during semantic search test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    asyncio.run(test_semantic_search()) 