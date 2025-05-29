#!/bin/bash
# Universal installation script for Reddit Meme Scraper
# Automatically detects platform and installs accordingly

set -e

echo "🚀 Reddit Meme Scraper - Quick Install"
echo "======================================"

# Function to check if we're on Raspberry Pi
is_raspberry_pi() {
    [[ -f /proc/device-tree/model ]] && grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null
}

# Function to install on Raspberry Pi (system-wide)
install_raspberry_pi() {
    echo "🍓 Raspberry Pi detected - Installing system-wide"
    
    # Update system
    echo "📦 Updating system packages..."
    sudo apt-get update
    
    # Install system dependencies
    echo "📦 Installing system dependencies..."
    sudo apt-get install -y python3-pip python3-dev git
    
    # Install Python packages system-wide
    echo "📦 Installing Python packages..."
    sudo pip3 install --break-system-packages \
        praw \
        requests \
        pillow \
        python-telegram-bot \
        schedule \
        httpx \
        python-dotenv
    
    # Install display libraries if SPI is available
    if [[ -e /dev/spidev0.0 ]] || [[ -e /sys/class/gpio ]]; then
        echo "🖥️  Installing display support..."
        sudo pip3 install --break-system-packages RPi.GPIO spidev
        
        # Install waveshare library
        echo "📱 Installing Waveshare e-ink library..."
        cd /tmp
        rm -rf e-Paper-master
        wget -q https://github.com/waveshare/e-Paper/archive/master.zip
        unzip -q master.zip
        cd e-Paper-master/RaspberryPi_JetsonNano/python
        sudo mkdir -p /usr/local/lib/python3.11/dist-packages/waveshare_epd
        sudo cp -r lib/waveshare_epd/* /usr/local/lib/python3.11/dist-packages/waveshare_epd/
        
        # Enable SPI
        echo "⚡ Enabling SPI interface..."
        sudo raspi-config nonint do_spi 0
        
        echo "✅ Display support installed"
    fi
    
    echo "✅ Raspberry Pi installation complete!"
    echo "💡 Display support enabled - edit config.json to use it"
}

# Function to install on regular Linux (with venv)
install_linux() {
    echo "🐧 Linux detected - Installing with virtual environment"
    
    # Check if python3-venv is available
    if ! python3 -m venv --help >/dev/null 2>&1; then
        echo "📦 Installing python3-venv..."
        sudo apt-get update
        sudo apt-get install -y python3-venv python3-pip
    fi
    
    # Create virtual environment
    echo "🏗️  Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    echo "📦 Installing Python packages..."
    pip install -r requirements.txt
    
    echo "✅ Linux installation complete!"
    echo "💡 Remember to activate venv: source venv/bin/activate"
}

# Main installation logic
main() {
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed"
        echo "Please install Python 3.7+ first"
        exit 1
    fi
    
    echo "✅ Python 3 found: $(python3 --version)"
    
    # Platform detection and installation
    if is_raspberry_pi; then
        install_raspberry_pi
    else
        install_linux
    fi
    
    # Run setup
    echo ""
    echo "🔧 Starting interactive setup..."
    if is_raspberry_pi; then
        python3 setup.py
    else
        if [[ -f venv/bin/activate ]]; then
            source venv/bin/activate
        fi
        python setup.py
    fi
    
    echo ""
    echo "🎉 Installation complete!"
    echo ""
    if is_raspberry_pi; then
        echo "To start the scraper:"
        echo "  python3 main.py"
        echo ""
        echo "To run as a service:"
        echo "  sudo systemctl enable reddit-meme-scraper"
        echo "  sudo systemctl start reddit-meme-scraper"
    else
        echo "To start the scraper:"
        echo "  source venv/bin/activate  # if not already activated"
        echo "  python main.py"
    fi
    echo ""
}

# Run main function
main "$@" 