#!/bin/bash

echo " Stopping Music Recommendation services..."
docker-compose down

echo ""
echo " All services stopped!"
echo ""
echo "To start again, run: ./scripts/start.sh"