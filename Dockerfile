# Use an official Python runtime as a parent image
# python:3.9-slim is smaller and safer than full images
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# git is often needed for installing python packages directly from github
# gcc and python3-dev are needed to compile tgcrypto for speed
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables (Optional default checks)
# PYTHONUNBUFFERED=1 prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]