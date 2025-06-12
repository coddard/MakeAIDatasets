import os
import logging
from pathlib import Path
from typing import Tuple, Dict
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract

logger = logging.getLogger(__name__)

def extract_pdf_metadata(reader: PdfReader) -> Dict[str, str]:
    """Extract metadata from PDF document"""
    meta = {}
    try:
        if reader.metadata:
            meta = {
                "title": reader.metadata.get("/Title", "").strip(),
                "author": reader.metadata.get("/Author", "").strip(),
                "creator": reader.metadata.get("/Creator", "").strip(),
                "producer": reader.metadata.get("/Producer", "").strip(),
                "creation_date": reader.metadata.get("/CreationDate", "").strip(),
                "modification_date": reader.metadata.get("/ModDate", "").strip()
            }
    except Exception as e:
        logger.warning(f"Metadata extraction failed: {str(e)}")
    return meta

def ocr_single_page(file_path: Path, page_number: int) -> str:
    """Perform OCR on a single PDF page"""
    try:
        images = convert_from_path(
            str(file_path),
            first_page=page_number,
            last_page=page_number,
            thread_count=2,
            poppler_path=os.getenv("POPPLER_PATH")
        )
        return pytesseract.image_to_string(images[0], lang='eng') if images else ""
    except Exception as e:
        logger.error(f"OCR failed for page {page_number}: {str(e)}")
        return ""

def process_pdf(file_path: Path) -> Tuple[str, bool, Dict]:
    """Process PDF file with text extraction and OCR fallback"""
    try:
        reader = PdfReader(str(file_path))
        pdf_meta = extract_pdf_metadata(reader)
        text_parts = []
        ocr_used = False
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text and len(page_text.strip()) > 20:
                    text_parts.append(page_text)
                    continue
            except Exception:
                pass
            
            logger.info(f"Using OCR for page {page_num}")
            ocr_text = ocr_single_page(file_path, page_num)
            if ocr_text:
                text_parts.append(ocr_text)
                ocr_used = True
            else:
                logger.warning(f"Page {page_num} extraction failed")
        
        return "\n".join(text_parts), ocr_used, pdf_meta
    except Exception as e:
        logger.error(f"PDF processing failed: {str(e)}")
        return "", False, {}