#!/bin/bash
set -e

echo "🛑 Stopping Music Recommendation API..."

# Stop and remove containers
docker-compose down

echo "🧹 Cleaning up..."
docker-compose down --volumes --remove-orphans

echo "✅ All services stopped and cleaned up!"