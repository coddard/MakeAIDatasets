# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build

# Copy only requirements file first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Download language model in builder stage
RUN mkdir -p /build/models && \
    apt-get update && \
    apt-get install -y wget && \
    wget -q https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz \
        -O /build/models/lid.176.ftz && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Runtime
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /install /usr/local
COPY --from=builder /build/models /app/models

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p input output/cleaned_texts output/metadata dataset web_uploads

# Copy application code
COPY src/ /app/src/
COPY setup.py .

# Install the package
RUN pip install -e .

# Set Python path and default port
ENV PYTHONPATH=/app
ENV PORT=5000

# Default command (can be overridden)
CMD ["python", "src/webapp.py"]

# Health check for web server
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1