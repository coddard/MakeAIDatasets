# MakeAIDatasets/Dockerfile

FROM python:3.10-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download language model
RUN mkdir -p /app/models \
    && wget -q https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz \
    -O /app/models/lid.176.ftz

FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /app/models /app/models

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p input output/cleaned_texts output/metadata dataset

# Default command
CMD ["python", "main.py"]