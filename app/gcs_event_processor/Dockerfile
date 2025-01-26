# Use the official Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Install required Python packages
RUN pip install --no-cache-dir flask google-cloud-storage google-cloud-bigquery requests

# Set environment variables
ENV PORT=8080

# Expose the port Flask will run on
EXPOSE 8080

# Command to run the Flask app
CMD ["python", "app.py"]
