# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for PDF processing and DB)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the current directory contents into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV FLASK_APP=wsgi.py
ENV FLASK_CONFIG=production

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "eventlet", "-w", "1", "wsgi:app"]
