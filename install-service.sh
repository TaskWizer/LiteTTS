#!/bin/bash
set -e

# LiteTTS Systemd Service Installation Script
# This script installs and enables the systemd service for automatic startup

echo "🔧 Installing LiteTTS systemd service..."

# Get the absolute path of the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="litetts"
SERVICE_FILE="$PROJECT_DIR/$SERVICE_NAME.service"

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

# Check if running as root for system installation
if [ "$EUID" -eq 0 ]; then
    # System-wide installation
    SYSTEM_DIR="/etc/systemd/system"
    echo "📁 Installing service to $SYSTEM_DIR"
    
    # Copy service file to system directory
    cp "$SERVICE_FILE" "$SYSTEM_DIR/"
    
    # Set proper permissions
    chmod 644 "$SYSTEM_DIR/$SERVICE_NAME.service"
    
    # Reload systemd daemon
    systemctl daemon-reload
    
    echo "✅ Service file installed to $SYSTEM_DIR"
    
else
    # User-level installation
    USER_DIR="$HOME/.config/systemd/user"
    echo "📁 Installing service to $USER_DIR"
    
    # Create directory if it doesn't exist
    mkdir -p "$USER_DIR"
    
    # Copy service file to user directory
    cp "$SERVICE_FILE" "$USER_DIR/"
    
    # Set proper permissions
    chmod 644 "$USER_DIR/$SERVICE_NAME.service"
    
    # Reload user systemd daemon
    systemctl --user daemon-reload
    
    echo "✅ Service file installed to $USER_DIR"
    echo "📝 Note: Make sure user lingering is enabled for startup on boot:"
    echo "   sudo loginctl enable-linger $USER"
fi

# Enable the service
echo "🚀 Enabling $SERVICE_NAME service..."
if [ "$EUID" -eq 0 ]; then
    systemctl enable "$SERVICE_NAME"
    echo "🔄 Starting $SERVICE_NAME service..."
    systemctl start "$SERVICE_NAME"
    echo "📊 Service status:"
    systemctl status "$SERVICE_NAME" --no-pager
else
    systemctl --user enable "$SERVICE_NAME"
    echo "🔄 Starting $SERVICE_NAME service..."
    systemctl --user start "$SERVICE_NAME"
    echo "📊 Service status:"
    systemctl --user status "$SERVICE_NAME" --no-pager
fi

echo ""
echo "✅ LiteTTS service installation complete!"
echo ""
echo "🌐 The API will be available at: http://localhost:8354"
echo "📊 Dashboard: http://localhost:8354/dashboard"
echo "📚 API Documentation: http://localhost:8354/docs"
echo ""
echo "🔧 Useful commands:"
if [ "$EUID" -eq 0 ]; then
    echo "  sudo systemctl status $SERVICE_NAME    # Check status"
    echo "  sudo systemctl restart $SERVICE_NAME  # Restart service"
    echo "  sudo systemctl stop $SERVICE_NAME     # Stop service"
    echo "  sudo journalctl -u $SERVICE_NAME -f  # View logs"
else
    echo "  systemctl --user status $SERVICE_NAME    # Check status"
    echo "  systemctl --user restart $SERVICE_NAME  # Restart service"
    echo "  systemctl --user stop $SERVICE_NAME     # Stop service"
    echo "  journalctl --user -u $SERVICE_NAME -f  # View logs"
fi
