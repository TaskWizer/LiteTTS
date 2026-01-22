#!/bin/bash
set -e

# LiteTTS Autostart Setup Script
# This script sets up LiteTTS to start automatically on login

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="run-background.sh"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/litetts.desktop"

echo "🔧 Setting up LiteTTS autostart..."

# Create autostart directory if it doesn't exist
mkdir -p "$AUTOSTART_DIR"

# Create desktop entry for autostart
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=LiteTTS API Server
Comment=High-performance ONNX-based Text-to-Speech API
Exec=$PROJECT_DIR/$SCRIPT_NAME start
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
StartupNotify=false
EOF

# Set proper permissions
chmod 644 "$DESKTOP_FILE"

echo "✅ Autostart entry created: $DESKTOP_FILE"
echo ""
echo "📝 LiteTTS will now start automatically when you log in"
echo ""
echo "🔧 Manual control:"
echo "  $PROJECT_DIR/$SCRIPT_NAME start    # Start manually"
echo "  $PROJECT_DIR/$SCRIPT_NAME stop     # Stop manually"
echo "  $PROJECT_DIR/$SCRIPT_NAME status   # Check status"
echo "  $PROJECT_DIR/$SCRIPT_NAME logs     # View logs"
echo ""
echo "🌐 After login, the API will be available at:"
echo "  http://localhost:8354"
echo "  http://localhost:8354/dashboard"
echo "  http://localhost:8354/docs"

# Also offer to create a crontab entry for more robust startup
echo ""
read -p "❓ Do you also want to add a crontab entry for additional reliability? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Create crontab entry
    CRON_ENTRY="@reboot sleep 30 && $PROJECT_DIR/$SCRIPT_NAME start > $PROJECT_DIR/cron.log 2>&1"
    
    # Check if entry already exists
    if crontab -l 2>/dev/null | grep -q "$PROJECT_DIR/$SCRIPT_NAME start"; then
        echo "⚠️ Crontab entry already exists"
    else
        # Add to crontab
        (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
        echo "✅ Crontab entry added"
    fi
fi

echo ""
echo "🎉 Autostart setup complete!"
echo ""
echo "📊 To test immediately:"
echo "  $PROJECT_DIR/$SCRIPT_NAME restart"
echo ""
echo "📝 To view logs:"
echo "  $PROJECT_DIR/$SCRIPT_NAME recent"
