#!/bin/bash

# OpenWebUI Deployment Script
# Sets up OpenWebUI with TLS, multiple API providers

# Configuration
DOMAIN="yourdomain.com"  # Change to your domain
EMAIL="admin@$DOMAIN"    # For Let's Encrypt notifications
OPENROUTER_API_KEY="your_openrouter_api_key"
GOOGLE_AI_STUDIO_API_KEY="your_google_ai_studio_api_key"
HUGGINGFACE_API_KEY="your_huggingface_api_key"
GROQ_API_KEY="your_groq_api_key"
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Create necessary directories
mkdir -p {data,certs}

# Generate docker-compose.yml
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: openwebui
    restart: unless-stopped
    ports:
      - "443:8080"
    volumes:
      - ./data:/app/backend/data
      - ./certs:/app/backend/certs
    environment:
      - WEBUI_SECRET_KEY=$SECRET_KEY
      - OLLAMA_API_BASE_URL=
      - OPENROUTER_API_BASE_URL=https://openrouter.ai/api/v1
      - OPENROUTER_API_KEY=$OPENROUTER_API_KEY
      - GOOGLE_AI_STUDIO_API_KEY=$GOOGLE_AI_STUDIO_API_KEY
      - HUGGINGFACE_API_KEY=$HUGGINGFACE_API_KEY
      - GROQ_API_KEY=$GROQ_API_KEY
      - DISABLE_SIGNUP=false
      - ENABLE_SIGNUP=false
      - WEBUI_AUTH=login
      - WEBUI_JWT_SECRET=$JWT_SECRET
      - WEBUI_HTTPS=true
      - WEBUI_CERT_FILE=/app/backend/certs/fullchain.pem
      - WEBUI_KEY_FILE=/app/backend/certs/privkey.pem
    networks:
      - webnet

networks:
  webnet:
    driver: bridge
EOF

# Check if certificates exist
if [ ! -f "./certs/fullchain.pem" ] || [ ! -f "./certs/privkey.pem" ]; then
    echo "No TLS certificates found. Would you like to:"
    echo "1) Use Let's Encrypt to generate new certificates (requires domain to be pointing to this server)"
    echo "2) Place your own certificates in the certs directory"
    echo "3) Continue without HTTPS (not recommended)"
    read -p "Enter choice [1-3]: " cert_choice

    case $cert_choice in
        1)
            echo "Setting up Let's Encrypt certificates..."
            sudo apt update
            sudo apt install -y certbot
            sudo certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m $EMAIL
            sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ./certs/
            sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ./certs/
            sudo chown -R $USER:$USER ./certs
            ;;
        2)
            echo "Please place your certificates in the certs directory as:"
            echo "- fullchain.pem"
            echo "- privkey.pem"
            echo "Then run this script again."
            exit 0
            ;;
        3)
            echo "Continuing without HTTPS (not recommended for production)"
            sed -i 's/WEBUI_HTTPS=true/WEBUI_HTTPS=false/' docker-compose.yml
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

# Start the container
echo "Starting OpenWebUI container..."
docker-compose up -d

echo ""
echo "OpenWebUI deployment complete!"
echo "Access your instance at: https://$DOMAIN"
echo ""
echo "Initial setup:"
echo "1. Visit the URL above"
echo "2. Create your first admin account"
echo "3. Configure your preferred models in settings"
