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
apt-get install -y -qq wget gnupg unzip curl

# Add Google Chrome repository
echo "Adding Google Chrome repository..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Update package list with Chrome repository
apt-get update -qq

# Install Chrome
echo "Installing Google Chrome..."
apt-get install -y -qq google-chrome-stable

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Verify installations
echo "Verifying installations..."
if [ -f "/usr/bin/google-chrome-stable" ]; then
    echo "✅ Chrome installed at /usr/bin/google-chrome-stable"
    google-chrome-stable --version
else
    echo "❌ Chrome not found at expected location"
    # Try to find Chrome in other locations
    CHROME_PATH=$(find /usr -name "*chrome*" -type f 2>/dev/null | grep -E "(chrome|chromium)" | head -1)
    if [ ! -z "$CHROME_PATH" ] && [ -f "$CHROME_PATH" ]; then
        echo "✅ Chrome found at alternative location: $CHROME_PATH"
        ln -sf "$CHROME_PATH" /usr/bin/google-chrome-stable
        echo "✅ Created symlink to /usr/bin/google-chrome-stable"
    else
        echo "❌ Chrome not found anywhere"
        exit 1
    fi
fi

if [ -f "/usr/local/bin/chromedriver" ]; then
    echo "✅ ChromeDriver installed at /usr/local/bin/chromedriver"
    /usr/local/bin/chromedriver --version
else
    echo "❌ ChromeDriver not found at expected location"
fi

# Set environment variables
echo "Setting environment variables..."
export CHROME_BIN=/usr/bin/google-chrome-stable
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Create environment file for persistence
echo "Creating environment file..."
echo "export CHROME_BIN=/usr/bin/google-chrome-stable" > $HOME/.chrome_env
echo "export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver" >> $HOME/.chrome_env

echo "Environment variables set:"
echo "CHROME_BIN=$CHROME_BIN"
echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

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
