# Backend Dockerfile — Python FastAPI
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    ghostscript \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and tools
COPY backend/ /app/backend/
COPY tools/ /app/tools/

# Set Python path to include root so imports work
ENV PYTHONPATH=/app:/app/backend

EXPOSE 8000

# Run the application
# Use shell form to expand environment variables
CMD sh -c "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"
