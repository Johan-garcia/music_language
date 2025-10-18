#!/bin/bash
set -e

echo "🎵 Starting Music Recommendation API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "  .env file not found. Creating from template..."
    cp .env.example .env
    echo " Please edit .env file with your API keys before running again."
    exit 1
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if API is responding
echo "🔍 Checking API health..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo " API is healthy!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Attempt $attempt/$max_attempts - waiting for API..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo " API failed to start properly"
    docker-compose logs api
    exit 1
fi

echo " Music API is running!"
echo " API Documentation: http://localhost:8000/docs"
echo " Health Check: http://localhost:8000/health"
echo " To stop: docker-compose down"