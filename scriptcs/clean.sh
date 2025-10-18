#!/bin/bash

echo " Cleaning Docker resources..."
echo ""

read -p "  This will remove all containers, volumes, and images. Continue? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping containers..."
    docker-compose down -v
    
    echo "Removing images..."
    docker-compose down --rmi all
    
    echo "Pruning system..."
    docker system prune -f
    
    echo ""
    echo " Cleanup complete!"
else
    echo " Cleanup cancelled."
fi