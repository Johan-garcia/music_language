#!/bin/bash

echo "🔨 Rebuilding all services..."
echo ""

# Stop services
echo "Stopping services..."
docker-compose down

# Rebuild
echo "Building images..."
docker-compose build --no-cache

# Start
echo "Starting services..."
docker-compose up -d

echo ""
echo " Rebuild complete!"
echo "Run ./scripts/status.sh to check services"