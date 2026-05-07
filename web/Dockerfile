# Dockerfile for Smart Resume Analyzer

# Use a more modern Python runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=run.py

# Set work directory
WORKDIR /app

# Install system dependencies (Optimized for Flask + AI)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libsqlite3-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    default-libmysqlclient-dev \
    poppler-utils \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python build tools first
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn eventlet

# Copy project
COPY . /app/

# Expose port
EXPOSE 5000

# Create directory for persistent SQLite database
RUN mkdir -p /app/backend/data

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]