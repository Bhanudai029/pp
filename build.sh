#!/usr/bin/env bash
# Build script for Render - installs Chrome/Chromium and sets up environment

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
apt-get install -y -qq wget gnupg unzip curl ca-certificates fonts-liberation \
  libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 \
  libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 \
  libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 \
  libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
  libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 \
  libxss1 libxtst6 lsb-release wget xdg-utils

# Add Google Chrome repository
echo "Adding Google Chrome repository..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Update package list with Chrome repository
apt-get update -qq

# Install Chrome
echo "Installing Google Chrome..."
apt-get install -y -qq google-chrome-stable

# Verify Chrome installation
echo "Verifying Chrome installation..."
if command -v google-chrome-stable &> /dev/null; then
    echo "✅ Chrome installed successfully"
    google-chrome-stable --version
    CHROME_BIN_PATH=$(which google-chrome-stable)
    echo "Chrome binary path: $CHROME_BIN_PATH"
else
    echo "❌ Chrome installation failed, trying Chromium..."
    apt-get install -y -qq chromium-browser
    if command -v chromium-browser &> /dev/null; then
        echo "✅ Chromium installed successfully"
        chromium-browser --version
        CHROME_BIN_PATH=$(which chromium-browser)
        echo "Chromium binary path: $CHROME_BIN_PATH"
    else
        echo "❌ Both Chrome and Chromium installation failed"
        exit 1
    fi
fi

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROME_VERSION=$($CHROME_BIN_PATH --version | awk '{print $3}' | cut -d'.' -f1)
if [ -z "$CHROME_VERSION" ]; then
    echo "❌ Could not determine Chrome version"
    exit 1
fi

echo "Chrome version: $CHROME_VERSION"

CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "❌ Could not determine ChromeDriver version"
    exit 1
fi

echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Verify ChromeDriver installation
echo "Verifying ChromeDriver installation..."
if [ -f "/usr/local/bin/chromedriver" ]; then
    echo "✅ ChromeDriver installed at /usr/local/bin/chromedriver"
    /usr/local/bin/chromedriver --version
else
    echo "❌ ChromeDriver not found at expected location"
    exit 1
fi

# Set environment variables for current session and future use
echo "Setting environment variables..."
export CHROME_BIN=$CHROME_BIN_PATH
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Create environment file for persistence
echo "Creating environment file..."
echo "export CHROME_BIN=$CHROME_BIN_PATH" > $HOME/.chrome_env
echo "export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver" >> $HOME/.chrome_env

echo "Environment variables set:"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

# Test Chrome and ChromeDriver
echo "Testing Chrome and ChromeDriver..."
if [ -f "$CHROME_BIN" ]; then
    echo "✅ Chrome binary exists at $CHROME_BIN"
else
    echo "❌ Chrome binary not found at $CHROME_BIN"
    exit 1
fi

if [ -f "$CHROMEDRIVER_PATH" ]; then
    echo "✅ ChromeDriver exists at $CHROMEDRIVER_PATH"
else
    echo "❌ ChromeDriver not found at $CHROMEDRIVER_PATH"
    exit 1
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
