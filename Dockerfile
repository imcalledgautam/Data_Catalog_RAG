# Backend Dockerfile for Bank Data Catalog API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r backend_requirements.txt

# Copy source code
COPY backend_api.py .
COPY src/ ./src/
COPY data/ ./data/
COPY config/ ./config/

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8080

# Run the FastAPI application
# Use PORT environment variable from Cloud Run, default to 8080
CMD uvicorn backend_api:app --host 0.0.0.0 --port ${PORT:-8080}
