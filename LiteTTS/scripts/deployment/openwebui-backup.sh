#!/bin/bash

# OpenWebUI Backup Script
# Backs up configuration, deployment settings, and data

# Configuration
BACKUP_DIR="./openwebui_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="openwebui_backup_$TIMESTAMP"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"  # If you're using environment variables in a separate file

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

echo "Starting OpenWebUI backup process..."

# 1. Backup Docker Compose file
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    cp "$DOCKER_COMPOSE_FILE" "$BACKUP_DIR/$BACKUP_NAME/"
    echo "✅ Docker compose file backed up"
else
    echo "⚠️  Docker compose file not found"
fi

# 2. Backup environment file (if exists)
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$BACKUP_DIR/$BACKUP_NAME/"
    echo "✅ Environment file backed up"
else
    echo "ℹ️  No environment file found"
fi

# 3. Backup data volume
if [ -d "./data" ]; then
    tar czf "$BACKUP_DIR/$BACKUP_NAME/data.tar.gz" ./data
    echo "✅ Application data backed up"
else
    echo "⚠️  Data directory not found"
fi

# 4. Backup certificates
if [ -d "./certs" ]; then
    tar czf "$BACKUP_DIR/$BACKUP_NAME/certs.tar.gz" ./certs
    echo "✅ TLS certificates backed up"
else
    echo "ℹ️  No certificates directory found"
fi

# Create a single archive
tar czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
rm -rf "$BACKUP_DIR/$BACKUP_NAME"

echo ""
echo "Backup completed successfully!"
echo "Backup file: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
