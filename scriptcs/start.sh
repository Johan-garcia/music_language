#!/bin/bash
set -e

echo "🎵 Starting Music Recommendation Full Stack..."
echo ""

# Check if .env file exists for backend
if [ ! -f fastapi_template/.env ]; then
    echo "  Backend .env file not found!"
    echo " Please run: cd fastapi_template && python setup_api_keys.py"
    exit 1
fi

# Build and start all services
echo " Building and starting Docker containers..."
docker-compose up --build -d

# Wait for database
echo " Waiting for database to be ready..."
sleep 5

# Wait for API
echo " Waiting for API to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo " API is healthy!"
        break
    fi
    attempt=$((attempt + 1))
    echo " Attempt $attempt/$max_attempts - waiting for API..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo " API failed to start"
    echo " Showing API logs:"
    docker-compose logs api
    exit 1
fi

# Wait for Frontend
echo " Waiting for Frontend to be ready..."
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:3000/health >/dev/null 2>&1; then
        echo " Frontend is healthy!"
        break
    fi
    attempt=$((attempt + 1))
    echo " Attempt $attempt/$max_attempts - waiting for Frontend..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "  Frontend might not be ready, check logs"
fi

echo ""
echo "════════════════════════════════════════════════"
echo " Full Stack is running!"
echo "════════════════════════════════════════════════"
echo ""
echo " Access points:"
echo "    Frontend:  http://localhost:3000"
echo "    API:       http://localhost:8000"
echo "    API Docs:  http://localhost:8000/docs"
echo "     Database:  localhost:5432"
echo ""
echo " Useful commands:"
echo "   View logs:        ./scripts/logs.sh"
echo "   Stop services:    ./scripts/stop.sh"
echo "   Restart:          ./scripts/restart.sh"
echo "   Status:           ./scripts/status.sh"
echo ""