# MakeAIDatasets/main.py

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
import concurrent.futures

from datasets import Dataset

from src.processors.pdf_processor import process_pdf
from src.processors.epub_processor import process_epub
from src.processors.text_cleaner import TextCleaner
from src.utils.filetype_detector import detect_file_type
from src.utils.summary_report import generate_summary_report

# Configuration constants
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
DATASET_DIR = Path("dataset")
META_DIR = OUTPUT_DIR / "metadata"
MODEL_DIR = Path("models")

# Ensure directories exist
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
DATASET_DIR.mkdir(exist_ok=True)
META_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def save_metadata(file: Path, metadata: Dict) -> bool:
    """Save processing metadata to JSON file"""
    try:
        meta_file = META_DIR / f"{file.stem}_metadata.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadata saved: {meta_file.name}")
        return True
    except Exception as e:
        logger.error(f"Metadata save failed: {str(e)}")
        return False

def save_cleaned_text(output_file, english_paragraphs, output_format="txt"):
    """Save cleaned text in the specified output format."""
    output_file.parent.mkdir(exist_ok=True)
    if output_format == "txt":
        with output_file.open('w', encoding='utf-8') as f:
            f.write("\n".join(english_paragraphs))
    elif output_format == "json":
        import json
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(english_paragraphs, f, ensure_ascii=False, indent=2)
    elif output_format == "csv":
        import csv
        with output_file.open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for p in english_paragraphs:
                writer.writerow([p])
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

def process_single_file(file: Path, text_cleaner: TextCleaner, output_format="txt") -> bool:
    """Process individual book file through the pipeline"""
    logger.info(f"Processing: {file.name}")
    
    # Initialize processing variables
    raw_text = ""
    ocr_used = False
    file_meta = {}
    source_format = detect_file_type(file)
    
    try:
        # File type routing
        if source_format == "pdf":
            raw_text, ocr_used, file_meta = process_pdf(file)
        elif source_format == "epub":
            raw_text = process_epub(file)
        else:
            logger.warning(f"Unsupported format: {file.name}")
            return False
    except Exception as e:
        logger.error(f"Processing failed for {file.name}: {str(e)}")
        return False
    
    # Text processing pipeline
    cleaned_paragraphs = text_cleaner.clean_text(raw_text)
    english_paragraphs = text_cleaner.filter_english(cleaned_paragraphs)
    english_ratio = f"{len(english_paragraphs)}/{len(cleaned_paragraphs)}"
    
    # Save cleaned text
    output_file = OUTPUT_DIR / "cleaned_texts" / f"{file.stem}_cleaned.{output_format}"
    try:
        save_cleaned_text(output_file, english_paragraphs, output_format)
        logger.info(f"Cleaned text saved: {output_file.name}")
    except Exception as e:
        logger.error(f"Text save failed: {str(e)}")
        return False
    
    # Generate and save metadata
    metadata = {
        "source_file": file.name,
        "source_format": source_format,
        "paragraph_count": len(english_paragraphs),
        "character_count": sum(len(p) for p in english_paragraphs),
        "english_ratio": english_ratio,
        "ocr_used": ocr_used,
        **file_meta
    }
    
    return save_metadata(file, metadata)

def process_batch_files(text_cleaner: TextCleaner, output_format="txt") -> bool:
    """Process all files in input directory with parallel execution"""
    files = [f for f in INPUT_DIR.iterdir() if f.is_file()]
    if not files:
        logger.info("No files found in input directory")
        return False
    
    logger.info(f"Processing {len(files)} files with {os.cpu_count()} workers")
    
    # Thread-based parallel processing
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=int(os.getenv("MAX_WORKERS", os.cpu_count()))
    ) as executor:
        futures = {
            executor.submit(process_single_file, file, text_cleaner, output_format): file
            for file in files
        }
        
        success_count = 0
        for future in concurrent.futures.as_completed(futures):
            file = futures[future]
            try:
                if future.result():
                    success_count += 1
            except Exception as e:
                logger.error(f"Error processing {file.name}: {str(e)}")
    
    logger.info(f"Completed {success_count}/{len(files)} files successfully")
    return success_count > 0

def build_hf_dataset() -> Optional[Dataset]:
    """Compile cleaned texts into Hugging Face dataset"""
    cleaned_files = list((OUTPUT_DIR / "cleaned_texts").glob("*_cleaned.txt"))
    if not cleaned_files:
        logger.warning("No cleaned files found for dataset creation")
        return None
    
    all_texts = []
    for file in cleaned_files:
        try:
            with file.open('r', encoding='utf-8') as f:
                all_texts.extend(line.strip() for line in f if line.strip())
        except Exception as e:
            logger.error(f"Error reading {file.name}: {str(e)}")
    
    if not all_texts:
        logger.error("No valid text collected for dataset")
        return None
    
    # Create and save dataset
    try:
        dataset = Dataset.from_dict({"text": all_texts})
        dataset.save_to_disk(str(DATASET_DIR))
        logger.info(f"Dataset saved with {len(all_texts)} samples")
        return dataset
    except Exception as e:
        logger.error(f"Dataset creation failed: {str(e)}")
        return None

def upload_to_hf_hub(dataset: Dataset) -> bool:
    """Upload dataset to Hugging Face Hub"""
    try:
        from huggingface_hub import login
        from datasets import DatasetDict
        
        token = os.getenv("HF_TOKEN") or input("Hugging Face API token: ")
        repo_id = input("Dataset repository ID (user/repo_name): ")
        
        login(token=token)
        DatasetDict({"train": dataset}).push_to_hub(repo_id)
        logger.info(f"Dataset uploaded to https://huggingface.co/datasets/{repo_id}")
        return True
    except ImportError:
        logger.error("huggingface_hub package not available")
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
    return False

def download_language_model():
    """Dummy implementation for compatibility. Lingua does not require model download."""
    logger.info("Lingua does not require a language model download. Returning None.")
    return None

def main(args=None):
    """Main execution pipeline for MakeAIDatasets"""
    logger.info("Starting MakeAIDatasets processing pipeline")
    import sys
    if args is None:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--lang", type=str, default="en")
        parser.add_argument("--output-format", type=str, choices=["txt", "json", "csv"], default="txt")
        args = parser.parse_args()
    # Initialize components
    text_cleaner = TextCleaner()
    # Processing stage
    output_format = getattr(args, "output_format", "txt")
    if hasattr(args, "process") and args.process:
        if not process_batch_files(text_cleaner, output_format=output_format):
            logger.error("Processing stage failed")
            return
        # After batch processing, generate summary report
        generate_summary_report(INPUT_DIR, OUTPUT_DIR, META_DIR)
    # Dataset creation stage
    if hasattr(args, "build_dataset") and args.build_dataset:
        dataset = build_hf_dataset()
        if dataset and hasattr(args, "upload_hf") and args.upload_hf:
            upload_to_hf_hub(dataset)
    logger.info("MakeAIDatasets pipeline completed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.exception(f"Fatal error: {str(e)}")