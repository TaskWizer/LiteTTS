#!/bin/bash

# Get latest change
git pull --force

# Stop and remove everything
docker compose down --volumes

# Purge all unused resources
docker system prune -af --volumes --force

# Start the service
docker compose up -d --build