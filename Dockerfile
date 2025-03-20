FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set working directory
WORKDIR /app

# Copy application files
COPY . /app

RUN apt-get update && apt-get install -y libpq-dev


# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the Prometheus port
EXPOSE 8000

# Set default config path
ENV METRIC_CONFIG_PATH=/config/metrics.json

# Run the application
CMD ["python", "app.py"]