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
sudo apt-get install -y python3-pip python3-pil python3-numpy git

# Enable SPI interface
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Download and install Waveshare e-Paper library
echo "Installing Waveshare e-ink display library..."
cd /tmp
rm -rf e-Paper-master
wget -q https://github.com/waveshare/e-Paper/archive/master.zip
unzip -q master.zip
cd e-Paper-master/RaspberryPi_JetsonNano/python

# Manual installation to avoid dependency issues
echo "Installing waveshare_epd manually..."
sudo mkdir -p /usr/local/lib/python3.11/dist-packages/waveshare_epd
sudo cp -r lib/waveshare_epd/* /usr/local/lib/python3.11/dist-packages/waveshare_epd/

# Install required dependencies manually
echo "Installing Python dependencies..."
pip3 install --user RPi.GPIO spidev pillow numpy

echo "Display setup complete!"
echo "To enable display, set 'display.enabled': true in config.json"
echo "Supported display types: epd2in13_V3, epd2in13_V4, epd2in7" 