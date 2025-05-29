#!/bin/bash
# Migration script: Switch from venv to system-wide installation on Raspberry Pi

set -e

echo "🔄 Migrating Reddit Meme Scraper to system-wide installation"
echo "============================================================"

# Check if we're on Raspberry Pi
if [[ ! -f /proc/device-tree/model ]] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "❌ This script is only for Raspberry Pi"
    exit 1
fi

# Stop the service if it's running
echo "🛑 Stopping reddit-meme-scraper service..."
sudo systemctl stop reddit-meme-scraper 2>/dev/null || echo "Service not running"

# Backup current setup
echo "💾 Creating backup..."
if [[ -d venv ]]; then
    tar -czf venv_backup_$(date +%Y%m%d_%H%M%S).tar.gz venv/ || true
fi

# Install system packages
echo "📦 Installing system-wide packages..."
sudo pip3 install --break-system-packages \
    praw \
    requests \
    pillow \
    python-telegram-bot \
    schedule \
    httpx \
    python-dotenv \
    RPi.GPIO \
    spidev

# Install display library if not already installed
if ! python3 -c "import waveshare_epd" 2>/dev/null; then
    echo "📱 Installing display library..."
    ./setup_display.sh
fi

# Update systemd service file
echo "⚙️  Updating systemd service..."
if [[ -f /etc/systemd/system/reddit-meme-scraper.service ]]; then
    sudo cp reddit-meme-scraper.service /etc/systemd/system/reddit-meme-scraper.service
    # Update paths for current user
    sudo sed -i "s|/home/pi/|$HOME/|g" /etc/systemd/system/reddit-meme-scraper.service
    sudo sed -i "s|User=pi|User=$USER|g" /etc/systemd/system/reddit-meme-scraper.service
    sudo sed -i "s|Group=pi|Group=$USER|g" /etc/systemd/system/reddit-meme-scraper.service
    sudo systemctl daemon-reload
fi

# Test the setup
echo "🧪 Testing system installation..."
if python3 -c "import praw, telegram, PIL; print('✅ Core packages OK')"; then
    echo "✅ Core packages working"
else
    echo "❌ Core packages test failed"
    exit 1
fi

if python3 -c "import waveshare_epd; print('✅ Display library OK')" 2>/dev/null; then
    echo "✅ Display library working"
else
    echo "⚠️  Display library not available (optional)"
fi

# Remove venv
echo "🗑️  Removing virtual environment..."
if [[ -d venv ]]; then
    read -p "Remove venv directory? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        rm -rf venv/
        echo "✅ Virtual environment removed"
    else
        echo "ℹ️  Virtual environment kept (you can remove it manually later)"
    fi
fi

# Start service
echo "🚀 Starting service..."
sudo systemctl start reddit-meme-scraper
sudo systemctl enable reddit-meme-scraper

echo ""
echo "🎉 Migration complete!"
echo ""
echo "Your meme scraper is now running system-wide:"
echo "  • No more venv activation needed"
echo "  • Direct python3 commands work"
echo "  • Simpler systemd service"
echo ""
echo "Check status: sudo systemctl status reddit-meme-scraper"
echo "View logs:    journalctl -u reddit-meme-scraper -f"
echo "" 