import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from pypdf import PdfReader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_pdf(pdf_path: str):
    logger.info(f"Analyzing PDF: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    logger.info(f"Total pages: {total_pages}")
    
    # Analyze first few pages in detail
    for i in range(min(3, total_pages)):
        page = reader.pages[i]
        text = page.extract_text()
        
        logger.info(f"\n=== Page {i+1} Analysis ===")
        logger.info(f"Text length: {len(text)} characters")
        logger.info(f"First 200 characters: {text[:200]}")
        
        # Check for common PDF issues
        if not text.strip():
            logger.warning(f"Page {i+1} has no text content")
        if len(text) < 100:
            logger.warning(f"Page {i+1} has very little text ({len(text)} chars)")
        
        # Check for special characters or encoding issues
        special_chars = set(char for char in text if ord(char) > 127)
        if special_chars:
            logger.info(f"Special characters found: {special_chars}")
        
        # Check for common formatting patterns
        if "\n\n" in text:
            logger.info("Double newlines found (paragraphs)")
        if "\t" in text:
            logger.info("Tabs found in text")
        
        # Check for common PDF artifacts
        if "" in text:
            logger.warning("Encoding issues detected ( character)")
        if "..." in text:
            logger.info("Ellipsis found (possible truncation)")

if __name__ == "__main__":
    pdf_path = "app/Manual de fallas V2 Oct24.pdf"
    analyze_pdf(pdf_path) 