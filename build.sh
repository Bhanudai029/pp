#!/usr/bin/env bash
# Build script for Render - uses Python to install Chrome/Chromium

echo "========================================"
echo "Starting build process for Render"
echo "========================================"
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "Home directory: $HOME"
echo "========================================"

# Install Python packages needed for Chrome installation
echo "Installing required Python packages..."
pip install --upgrade pip
pip install requests

# Run Python installation script
echo "Running Chrome installation script..."
python3 install_chrome.py

# Source the environment variables if the file exists
if [ -f "$HOME/.chrome_env" ]; then
    echo "Loading Chrome environment variables..."
    source "$HOME/.chrome_env"
    
    # Also export them for the current session
    export CHROME_BIN
    export CHROMEDRIVER_PATH
    export PATH
    
    echo "Environment variables loaded:"
    echo "CHROME_BIN=$CHROME_BIN"
    echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"
fi

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
