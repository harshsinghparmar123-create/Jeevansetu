FROM python:3.13-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port
EXPOSE 8000

# Set executable permissions on entrypoint script
RUN chmod +x docker-entrypoint.sh

# Use entrypoint to run migrations and start server
ENTRYPOINT ["./docker-entrypoint.sh"]
