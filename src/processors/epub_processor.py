import logging
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def process_epub(file_path: Path) -> str:
    """Extract and process text from EPUB file"""
    try:
        book = epub.read_epub(str(file_path))
        text_parts = []
        
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                try:
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text with paragraph preservation
                    text = soup.get_text(separator="\n", strip=True)
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"EPUB item processing error: {str(e)}")
        
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.error(f"EPUB processing failed: {str(e)}")
        return ""