#!/usr/bin/env/bash
set -o errexit  # Exit on any error
set -o xtrace   # Show all commands being executed for debugging

echo "========================================"
echo "Starting build process for Render"
echo "========================================"
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "Home directory: $HOME"
echo "System info:"
uname -a
echo "========================================"

# Install system dependencies
echo "Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq wget unzip curl gnupg software-properties-common apt-transport-https ca-certificates

# Function to install Google Chrome with multiple methods
install_google_chrome() {
    echo "Attempting to install Google Chrome..."
    
    # Method 1: Using official Google repository
    echo "Method 1: Official Google repository"
    if ! wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -; then
        echo "Failed to add Google signing key"
    fi
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    apt-get update -qq
    
    if apt-get install -y -qq google-chrome-stable; then
        if command -v google-chrome-stable &> /dev/null; then
            echo "✅ Google Chrome installed successfully via repository"
            CHROME_PATH=$(which google-chrome-stable)
            echo "Chrome path: $CHROME_PATH"
            google-chrome-stable --version
            return 0
        fi
    fi
    
    # Method 2: Direct download and install
    echo "Method 2: Direct download"
    wget -O /tmp/google-chrome-stable_current_amd64.deb "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
    if dpkg -i /tmp/google-chrome-stable_current_amd64.deb; then
        apt-get install -f -y  # Fix any dependency issues
        if command -v google-chrome-stable &> /dev/null; then
            echo "✅ Google Chrome installed successfully via direct download"
            CHROME_PATH=$(which google-chrome-stable)
            echo "Chrome path: $CHROME_PATH"
            google-chrome-stable --version
            return 0
        fi
    fi
    
    echo "❌ Google Chrome installation failed with all methods"
    return 1
}

# Function to install Chromium as fallback
install_chromium() {
    echo "Installing Chromium as fallback..."
    apt-get update -qq
    if apt-get install -y -qq chromium-browser; then
        if command -v chromium-browser &> /dev/null; then
            echo "✅ Chromium installed successfully"
            CHROME_PATH=$(which chromium-browser)
            echo "Chromium path: $CHROME_PATH"
            chromium-browser --version
            return 0
        fi
    fi
    echo "❌ Chromium installation failed"
    return 1
}

# Try to install Chrome
CHROME_BIN_PATH=""
if ! install_google_chrome; then
    echo "Google Chrome installation failed, trying Chromium..."
    if ! install_chromium; then
        echo "❌ All Chrome installation methods failed"
        echo "Checking what Chrome packages are available..."
        apt-cache search chrome || echo "No chrome packages found"
        echo "Listing all installed packages:"
        dpkg -l | grep -i chrome || echo "No Chrome packages installed"
        exit 1
    else
        CHROME_BIN_PATH=$(which chromium-browser)
    fi
else
    CHROME_BIN_PATH=$(which google-chrome-stable)
fi

# Verify Chrome is actually executable
if [ -n "$CHROME_BIN_PATH" ] && [ -x "$CHROME_BIN_PATH" ]; then
    echo "✅ Chrome binary is executable: $CHROME_BIN_PATH"
    $CHROME_BIN_PATH --version || echo "Warning: Could not get Chrome version"
else
    echo "❌ Chrome binary not found or not executable"
    echo "PATH: $PATH"
    which google-chrome-stable || echo "google-chrome-stable not found in PATH"
    which chromium-browser || echo "chromium-browser not found in PATH"
    exit 1
fi

# Create environment file
echo "# Chrome environment variables" > $HOME/.chrome_env
echo "export CHROME_BIN=$CHROME_BIN_PATH" >> $HOME/.chrome_env
echo "export RENDER=true" >> $HOME/.chrome_env

# Set for current session
export CHROME_BIN=$CHROME_BIN_PATH
export RENDER=true

echo "Environment variables set:"
echo "CHROME_BIN=$CHROME_BIN_PATH"

# Install ChromeDriver
echo "Installing ChromeDriver..."
if [ -n "$CHROME_BIN_PATH" ]; then
    CHROME_VERSION=$($CHROME_BIN_PATH --version 2>/dev/null | awk '{print $3}' | cut -d'.' -f1)
    if [ -n "$CHROME_VERSION" ]; then
        CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
        if [ -n "$CHROMEDRIVER_VERSION" ]; then
            wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
            unzip /tmp/chromedriver.zip -d /usr/local/bin/
            chmod +x /usr/local/bin/chromedriver
            echo "✅ ChromeDriver installed at /usr/local/bin/chromedriver"
            echo "export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver" >> $HOME/.chrome_env
            export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
        fi
    fi
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