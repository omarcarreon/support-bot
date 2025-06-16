from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class ManualTextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

    def split_text(self, text: str, filename: str = None) -> List[Document]:
        """
        Split text into chunks.
        
        Args:
            text: The text to split
            filename: Optional filename for metadata
            
        Returns:
            List of Document objects containing the chunks
        """
        print(f"Input text length: {len(text)} characters")
        
        documents = self.text_splitter.create_documents([text])
        
        print(f"Created {len(documents)} chunks")
        
        for i, doc in enumerate(documents):
            page_number = 0
            section = ""
            
            # Extract page number
            if "--- Page" in doc.page_content:
                try:
                    page_text = doc.page_content.split("--- Page")[1].split("---")[0].strip()
                    page_number = int(page_text)
                except (ValueError, IndexError):
                    pass
            
            # Try to extract section from content
            content_lines = doc.page_content.split("\n")
            for line in content_lines[:3]:  # Look in first 3 lines
                if line.strip() and not line.startswith("---"):
                    section = line.strip()
                    break
            
            print(f"Chunk {i+1}: {len(doc.page_content)} characters")
            
            # Ensure all metadata values are of the correct type
            doc.metadata.update({
                "chunk_number": int(i),
                "total_chunks": int(len(documents)),
                "page": int(page_number),
                "section": str(section),
                "filename": str(filename or "")
            })
            
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of documents into chunks.
        
        Args:
            documents: List of Document objects to split
            
        Returns:
            List of Document objects containing the chunks
        """
        return self.text_splitter.split_documents(documents) 