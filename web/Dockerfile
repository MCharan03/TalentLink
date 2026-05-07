# Dockerfile for Smart Resume Analyzer

# Use official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (e.g., for PDF parsing, database drivers)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install gunicorn

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