FROM python:3.11-slim

# System dependencies needed by PyMuPDF (fitz), Pillow, and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching — only reinstalls if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Render provides $PORT at runtime — default to 8000 for local testing
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main_api:app --host 0.0.0.0 --port ${PORT}"]