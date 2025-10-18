#!/bin/bash

echo " Viewing Docker logs (Ctrl+C to exit)..."
echo ""

if [ -z "$1" ]; then
    # Show all logs
    docker-compose logs -f
else
    # Show specific service logs
    docker-compose logs -f "$1"
fi