from pathlib import Path
import mimetypes
import logging

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def detect_file_type(file_path: Path) -> str:
    """Returns the file type based on extension and mime type."""
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return "unknown"
        
    try:
        mime, _ = mimetypes.guess_type(str(file_path))
        ext = file_path.suffix.lower()
        
        if ext == ".pdf" or (mime and "pdf" in mime):
            return "pdf"
        if ext == ".epub" or (mime and "epub" in mime):
            return "epub"
        if ext == ".txt" or (mime and "text" in mime):
            return "txt"
        if ext == ".docx" or (mime and "word" in mime):
            return "docx"
        if ext == ".html" or ext == ".htm" or (mime and "html" in mime):
            return "html"
        
        logger.warning(f"Unrecognized file type for {file_path}")
        return "unknown"
        
    except Exception as e:
        logger.error(f"Error detecting file type: {str(e)}")
        return "unknown"
