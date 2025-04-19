# Use the official Python image from Docker Hub
FROM python:3.12-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libcups2 \
    && apt-get clean

# Install Playwright and browser binaries
RUN pip install playwright
RUN playwright install

# Set the working directory inside the container
WORKDIR /app

# Copy your project files into the container
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Command to run your Flask app
CMD ["python", "app.py"]
