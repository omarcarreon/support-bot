import os
from typing import Tuple
from pypdf import PdfReader

class PDFValidator:
    # Maximum file size in bytes (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'application/x-pdf',
        'application/octet-stream'
    ]

    @classmethod
    def validate_file(cls, file_path: str) -> Tuple[bool, str]:
        """
        Validate a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, "File does not exist"

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > cls.MAX_FILE_SIZE:
                return False, f"File size exceeds maximum limit of {cls.MAX_FILE_SIZE / (1024 * 1024)}MB"

            # Check if file is a valid PDF
            try:
                reader = PdfReader(file_path)
                if len(reader.pages) == 0:
                    return False, "PDF file is empty"
            except Exception as e:
                return False, f"Invalid PDF file: {str(e)}"

            return True, ""

        except Exception as e:
            return False, f"Error validating PDF: {str(e)}"

    @classmethod
    def validate_mime_type(cls, mime_type: str) -> bool:
        """
        Validate the MIME type of a file.
        
        Args:
            mime_type: MIME type to validate
            
        Returns:
            bool: True if MIME type is allowed
        """
        return mime_type.lower() in cls.ALLOWED_MIME_TYPES 