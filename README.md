# MakeAIDatasets

## Project Overview
MakeAIDatasets is an automated pipeline for creating high-quality text datasets from PDF and EPUB sources. The system automates text extraction, language filtering, and dataset preparation, and generates comprehensive metadata for quality control.

## Key Features
- **Multi-format support**: Process PDF (text & scanned) and EPUB files
- **Intelligent text extraction**: Native text extraction with OCR fallback
- **Language filtering**: FastText-powered English detection with confidence thresholds
- **Metadata enrichment**: Extract technical and contextual metadata
- **Parallel processing**: Utilize multi-core CPUs for efficient batch processing
- **Dataset export**: Create Hugging Face-compatible datasets with one command
- **Cloud integration**: Direct upload to Hugging Face Hub

## Technical Process
1. **Input Handling**
   - Accepts PDF and EPUB files in `/input` directory
   - Processes files in parallel using thread pooling

2. **Content Extraction**
   - **PDF**: Native text extraction with PyPDF2 + OCR fallback using Tesseract
   - **EPUB**: Structural parsing with ebooklib and BeautifulSoup

3. **Text Processing**
   - Whitespace normalization
   - Short line filtering
   - Language detection (English with >70% confidence)
   - Paragraph reconstruction

4. **Metadata Generation**
   - File characteristics (format, size)
   - Processing details (OCR usage, page count)
   - Content metrics (paragraph count, English ratio)
   - PDF metadata (title, author, creation date)

5. **Output Creation**
   - Cleaned text files in `/output/cleaned_texts`
   - JSON metadata in `/output/metadata`
   - Hugging Face dataset in `/hf_dataset`

## Repository Structure
```
MakeAIDatasets/
├── input/                  # Source files directory
├── output/                 # Processing results
│   ├── cleaned_texts/      # Processed text files
│   └── metadata/           # JSON metadata files
├── hf_dataset/             # Hugging Face dataset
├── src/                    # Application source code
│   ├── main.py             # Main processing script
│   ├── processors/         # Processing modules
│   │   ├── pdf_processor.py
│   │   ├── epub_processor.py
│   │   └── text_cleaner.py
│   └── utils/              # Utility functions
├── tests/                  # Test cases
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment configuration
└── README.md               # Project documentation
```

## Requirements
### Python Dependencies (requirements.txt)
```text
PyPDF2==3.0.0
ebooklib==1.0.0
beautifulsoup4==4.12.0
datasets==2.14.0
pdf2image==1.16.0
pytesseract==0.3.10
fasttext==0.9.2
requests==2.31.0
huggingface-hub==0.16.4
python-dotenv==1.0.0
tqdm==4.66.1
```

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    tesseract-ocr-eng
```

## Docker Setup
### Dockerfile
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p input output

# Run processing
CMD ["python", "src/main.py"]
```

## Usage
### Basic Processing
1. Place source files in `/input` directory
2. Run main processing:
   ```bash
   python src/main.py
   ```
3. Follow interactive prompts for dataset creation

### Advanced Options
```bash
# Process files without interaction
python src/main.py --auto

# Set custom directories
python src/main.py --input custom_input --output custom_output

# Enable debug logging
python src/main.py --log-level DEBUG
```

### Docker Execution
```bash
# Build Docker image
docker build -t book-processor .

# Run container with volume mounts
docker run -it --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  book-processor
  
# With environment variables
docker run -it --rm \
  -e POPPLER_PATH=/custom/path \
  -e MIN_ENGLISH_CONFIDENCE=0.8 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  book-processor
```

## Command Line Usage

- Process all input files and generate summary report:
  ```bash
  python -m src.cli --process
  ```
- Build Hugging Face dataset:
  ```bash
  python -m src.cli --build-dataset
  ```
- Upload dataset to Hugging Face Hub:
  ```bash
  python -m src.cli --build-dataset --upload-hf
  ```
- Process with different output format:
  ```bash
  python -m src.cli --process --output-format json
  ```

## Web Interface

- Start the web interface:
  ```bash
  python src/webapp.py
  ```
- Go to `http://localhost:5000` in your browser and upload a file.

## Testing

- Run all tests:
  ```bash
  pytest
  ```

## Advanced Features

- Multi-language support via `--lang` parameter.
- After batch processing, check `output/summary_report.json` for summary statistics.
- Output can be exported in different formats: txt, json, csv.

## Errors and Logging

- Logs can be written to both console and file (can be improved).
- Failed files are listed in summary_report.json.

## Contribution and Development

- Add tests for every function.
- CI/CD with GitHub Actions is recommended.
- Update README and examples regularly.

## Configuration
Customize processing through environment variables (use `.env` file or export):

| Variable | Default | Description |
|----------|---------|-------------|
| `POPPLER_PATH` | System PATH | Custom Poppler binaries location |
| `TESSERACT_THREADS` | 4 | OCR processing threads |
| `MIN_ENGLISH_CONFIDENCE` | 0.7 | Language detection threshold |
| `HF_TOKEN` | - | Hugging Face API token |
| `LOGLEVEL` | INFO | Log verbosity |
| `MAX_WORKERS` | CPU cores | Thread pool size |

## Output Structure
```
output/
├── cleaned_texts/
│   ├── book1_cleaned.txt
│   └── book2_cleaned.txt
├── metadata/
│   ├── book1_metadata.json
│   └── book2_metadata.json
└── hf_dataset/
    ├── dataset_info.json
    ├── state.json
    └── data/
        └── train.arrow
```

Sample metadata:
```json
{
  "source_file": "deep_learning.pdf",
  "source_format": ".pdf",
  "paragraph_count": 1242,
  "character_count": 687412,
  "english_ratio": "1242/1248",
  "ocr_used": true,
  "title": "Deep Learning Textbook",
  "author": "Ian Goodfellow et al.",
  "creation_date": "D:20230115120000Z"
}
```

## Planned Features
### Near-term Roadmap
- [ ] EPUB chapter preservation
- [ ] Automatic quality scoring
- [ ] Kaggle API integration
- [ ] Docker image optimization
- [ ] PDF text/OCR hybrid mode

### Future Development
- [ ] Distributed processing with Celery
- [ ] AWS S3 integration
- [ ] Content deduplication
- [ ] Topic classification
- [ ] Readability metrics
- [ ] REST API interface

## Contribution Guidelines
We welcome contributions! Here's how to help:
1. Report issues and suggest features
2. Submit pull requests:
   - Fork repository
   - Create feature branch (`feat/new-feature`)
   - Submit PR with detailed description
3. Improve documentation
4. Add test cases

### Testing Requirements
- Unit tests for all processing modules
- Integration tests with sample books
- Performance benchmarks
- Error handling simulations

## Support
For assistance, please:
- Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Open a GitHub issue

