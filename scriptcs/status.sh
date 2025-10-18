#!/bin/bash

echo "🔄 Restarting Music Recommendation services..."
echo ""

if [ -z "$1" ]; then
    # Restart all services
    echo "Restarting all services..."
    docker-compose restart
else
    # Restart specific service
    echo "Restarting $1..."
    docker-compose restart "$1"
fi

echo ""
echo "✅ Services restarted!"