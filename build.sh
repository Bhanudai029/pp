#!/usr/bin/env bash
# Build script for Render - installs Chrome/Chromium and sets up environment

echo "========================================"
echo "Starting build process for Render"
echo "========================================"
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "Home directory: $HOME"
echo "========================================"

# Function to install Chrome
install_chrome() {
    echo "Installing Google Chrome..."
    
    # Add Google Chrome repository
    echo "Adding Google Chrome repository..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - 2>/dev/null || curl -s https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    
    # Update package list
    apt-get update -qq
    
    # Install Chrome
    apt-get install -y -qq google-chrome-stable
    
    # Verify installation
    if command -v google-chrome-stable &> /dev/null; then
        echo "✅ Google Chrome installed successfully"
        CHROME_PATH=$(which google-chrome-stable)
        echo "Chrome path: $CHROME_PATH"
        google-chrome-stable --version
        echo "export CHROME_BIN=$CHROME_PATH" >> $HOME/.chrome_env
        echo "export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver" >> $HOME/.chrome_env
        return 0
    else
        echo "❌ Google Chrome installation failed"
        return 1
    fi
}

# Function to install Chromium as fallback
install_chromium() {
    echo "Installing Chromium as fallback..."
    
    # Update package list
    apt-get update -qq
    
    # Install Chromium
    apt-get install -y -qq chromium-browser chromium-chromedriver
    
    # Verify installation
    if command -v chromium-browser &> /dev/null; then
        echo "✅ Chromium installed successfully"
        CHROMIUM_PATH=$(which chromium-browser)
        echo "Chromium path: $CHROMIUM_PATH"
        chromium-browser --version
        echo "export CHROME_BIN=$CHROMIUM_PATH" >> $HOME/.chrome_env
        echo "export CHROMEDRIVER_PATH=$(which chromedriver)" >> $HOME/.chrome_env
        return 0
    else
        echo "❌ Chromium installation failed"
        return 1
    fi
}

# Install system dependencies
echo "Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq wget curl gnupg unzip ca-certificates \
  fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
  libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 \
  libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 \
  libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 \
  libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
  libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 \
  libxtst6 lsb-release xdg-utils

# Create environment file
echo "# Chrome environment variables" > $HOME/.chrome_env
echo "export RENDER=true" >> $HOME/.chrome_env

# Try to install Chrome first
if ! install_chrome; then
    echo "Chrome installation failed, trying Chromium..."
    if ! install_chromium; then
        echo "❌ Both Chrome and Chromium installation failed"
        exit 1
    fi
fi

# Install ChromeDriver (only if we installed Chrome, not Chromium)
if command -v google-chrome-stable &> /dev/null; then
    echo "Installing ChromeDriver for Chrome..."
    CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | cut -d'.' -f1)
    if [ ! -z "$CHROME_VERSION" ]; then
        CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
        if [ ! -z "$CHROMEDRIVER_VERSION" ]; then
            wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
            unzip /tmp/chromedriver.zip -d /usr/local/bin/
            chmod +x /usr/local/bin/chromedriver
            rm /tmp/chromedriver.zip
            echo "✅ ChromeDriver installed at /usr/local/bin/chromedriver"
            /usr/local/bin/chromedriver --version
        fi
    fi
fi

# Test the installed browser
echo "Testing installed browser..."
source $HOME/.chrome_env
if [ ! -z "$CHROME_BIN" ] && [ -f "$CHROME_BIN" ]; then
    echo "✅ Chrome binary exists at $CHROME_BIN"
    echo "Browser version: $($CHROME_BIN --version)"
else
    echo "❌ Chrome binary not found"
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
echo "Chrome binary path: $CHROME_BIN"
echo "ChromeDriver path: $CHROMEDRIVER_PATH"
echo "Environment file: $HOME/.chrome_env"
