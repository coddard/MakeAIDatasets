import logging
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def process_html(file_path: Path) -> str:
    """Extract and process text from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator="\n", strip=True)
            return text
    except Exception as e:
        logger.error(f"HTML processing failed: {str(e)}")
        return ""
