#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for database to start..."
# Simple sleep or check for database availability could go here, or handled by docker-compose depends_on

echo "Pre-training AI Model..."
python app/ai/train.py

echo "Running Database Migrations..."
alembic upgrade head

echo "Starting Uvicorn Server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
