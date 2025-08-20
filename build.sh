#!/usr/bin/env bash
# Build script for Render - installs Chromium following Render community guidelines

echo "========================================"
echo "Starting build process for Render"
echo "========================================"
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "Home directory: $HOME"
echo "========================================"

# Install system dependencies
echo "Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq wget unzip curl

# Install Chromium following Render community guidelines
echo "Installing Chromium..."
cd /tmp
wget https://download-chromium.appspot.com/dl/Linux_x64?type=snapshots -O chrome-linux.zip
unzip chrome-linux.zip
mkdir -p /opt/render/project/.render/chrome
cp -r chrome-linux/* /opt/render/project/.render/chrome/

# Verify installation
if [ -f "/opt/render/project/.render/chrome/chrome" ]; then
    echo "✅ Chromium installed successfully"
    echo "Chromium path: /opt/render/project/.render/chrome/chrome"
    
    # Create environment file with the correct path
    echo "# Chrome environment variables" > $HOME/.chrome_env
    echo "export CHROME_BIN=/opt/render/project/.render/chrome/chrome" >> $HOME/.chrome_env
    echo "export RENDER=true" >> $HOME/.chrome_env
    
    # Also set for current session
    export CHROME_BIN=/opt/render/project/.render/chrome/chrome
    export RENDER=true
    
    echo "Environment variables set:"
    echo "CHROME_BIN=$CHROME_BIN"
else
    echo "❌ Chromium installation failed"
    exit 1
fi

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
if [ ! -z "$CHROMEDRIVER_VERSION" ]; then
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip /tmp/chromedriver.zip -d /opt/render/project/.render/chrome/
    chmod +x /opt/render/project/.render/chrome/chromedriver
    rm /tmp/chromedriver.zip
    
    if [ -f "/opt/render/project/.render/chrome/chromedriver" ]; then
        echo "✅ ChromeDriver installed at /opt/render/project/.render/chrome/chromedriver"
        echo "export CHROMEDRIVER_PATH=/opt/render/project/.render/chrome/chromedriver" >> $HOME/.chrome_env
        export CHROMEDRIVER_PATH=/opt/render/project/.render/chrome/chromedriver
        echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"
    else
        echo "❌ ChromeDriver installation failed"
    fi
else
    echo "❌ Could not determine ChromeDriver version"
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