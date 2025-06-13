import logging
from pathlib import Path
from docx import Document

logger = logging.getLogger(__name__)

def process_docx(file_path: Path) -> str:
    """Extract and process text from DOCX file"""
    try:
        doc = Document(str(file_path))
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.error(f"DOCX processing failed: {str(e)}")
        return ""
