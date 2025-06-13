import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def process_txt(file_path: Path) -> str:
    """Read and return text from TXT file"""
    try:
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return ""
            
        if file_path.stat().st_size == 0:
            logger.warning(f"Empty file: {file_path}")
            return ""
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.strip():
            logger.warning(f"File contains only whitespace: {file_path}")
            return ""
            
        return content
        
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decode error in {file_path}: {str(e)}")
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e2:
            logger.error(f"Failed to read with latin-1 encoding: {str(e2)}")
            return ""
    except Exception as e:
        logger.error(f"TXT processing failed: {str(e)}")
        return ""
