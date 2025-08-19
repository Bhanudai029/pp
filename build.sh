#!/usr/bin/env bash
# exit on error
set -o errexit

echo "========================================"
echo "Starting build process for Render"
echo "========================================"

# Run the Python Chrome installer
echo "Running Chrome installation script..."
python3 install_chrome.py

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create downloads directory
mkdir -p downloads
chmod 777 downloads

echo "========================================"
echo "Build completed successfully!"
echo "========================================"
