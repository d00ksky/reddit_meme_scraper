#!/bin/bash
# Setup script for e-ink display support on Raspberry Pi
# This is optional - the app will work without display support

echo "Setting up e-ink display support for Raspberry Pi..."

# Check if we're on a Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Not running on Raspberry Pi. Skipping display setup."
    exit 0
fi

# Enable SPI interface
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy

# Install Waveshare e-ink display library
echo "Installing Waveshare e-ink library..."
cd /tmp
wget https://github.com/waveshare/e-Paper/archive/master.zip
unzip master.zip
cd e-Paper-master/RaspberryPi_JetsonNano/python/
sudo python3 setup.py install

echo "Display setup complete!"
echo "To enable display, set 'display.enabled': true in config.json"
echo "Supported display types: epd2in13_V3, epd2in7" 