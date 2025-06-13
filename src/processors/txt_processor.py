import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def process_txt(file_path: Path) -> str:
    """Read and return text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"TXT processing failed: {str(e)}")
        return ""
