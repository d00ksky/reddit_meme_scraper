#!/bin/bash
# Setup script for e-ink display support on Raspberry Pi
# This is optional - the app will work without display support

echo "Setting up e-ink display support for Raspberry Pi..."

# Check if running on Raspberry Pi
if [[ ! -f /proc/device-tree/model ]] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Not running on Raspberry Pi. Skipping display setup."
    exit 0
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy git python3-dev

# Enable SPI interface
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Check if we're in a virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "Installing in virtual environment: $VIRTUAL_ENV"
    PYTHON_CMD="python"
    PIP_CMD="pip"
    LIB_PATH="$VIRTUAL_ENV/lib/python3.11/site-packages"
else
    echo "No virtual environment detected, using system Python"
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
    LIB_PATH="/usr/local/lib/python3.11/dist-packages"
fi

# Download and install Waveshare e-Paper library
echo "Installing Waveshare e-ink display library..."
cd /tmp
rm -rf e-Paper-master
wget -q https://github.com/waveshare/e-Paper/archive/master.zip
unzip -q master.zip
cd e-Paper-master/RaspberryPi_JetsonNano/python

# Manual installation to avoid dependency issues
echo "Installing waveshare_epd manually to: $LIB_PATH"
mkdir -p "$LIB_PATH/waveshare_epd"
cp -r lib/waveshare_epd/* "$LIB_PATH/waveshare_epd/"

# Install required dependencies
echo "Installing Python dependencies..."
if [[ -n "$VIRTUAL_ENV" ]]; then
    $PIP_CMD install RPi.GPIO spidev pillow numpy
else
    $PIP_CMD install --user RPi.GPIO spidev pillow numpy --break-system-packages
fi

echo "Display setup complete!"
echo "To enable display, set 'display.enabled': true in config.json"
echo "Supported display types: epd2in13_V3, epd2in13_V4, epd2in7" 