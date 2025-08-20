#!/usr/bin/env bash
# Build script for Render - installs Chrome/Chromium with multiple fallback strategies

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
apt-get install -y -qq wget unzip curl gnupg

# Function to install Google Chrome
install_google_chrome() {
    echo "Installing Google Chrome..."
    
    # Add Google Chrome repository
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
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
        return 0
    else
        echo "❌ Google Chrome installation failed"
        return 1
    fi
}

# Function to install Chromium (fallback)
install_chromium() {
    echo "Installing Chromium as fallback..."
    
    # Update package list
    apt-get update -qq
    
    # Install Chromium
    apt-get install -y -qq chromium-browser
    
    # Verify installation
    if command -v chromium-browser &> /dev/null; then
        echo "✅ Chromium installed successfully"
        CHROMIUM_PATH=$(which chromium-browser)
        echo "Chromium path: $CHROMIUM_PATH"
        chromium-browser --version
        return 0
    else
        echo "❌ Chromium installation failed"
        return 1
    fi
}

# Try to install Google Chrome first
if ! install_google_chrome; then
    echo "Google Chrome installation failed, trying Chromium..."
    if ! install_chromium; then
        echo "❌ Both Google Chrome and Chromium installation failed"
        exit 1
    else
        # Chromium installed successfully
        CHROME_BIN_PATH=$(which chromium-browser)
    fi
else
    # Google Chrome installed successfully
    CHROME_BIN_PATH=$(which google-chrome-stable)
fi

# Create environment file with the correct path
echo "# Chrome environment variables" > $HOME/.chrome_env
echo "export CHROME_BIN=$CHROME_BIN_PATH" >> $HOME/.chrome_env
echo "export RENDER=true" >> $HOME/.chrome_env

# Also set for current session
export CHROME_BIN=$CHROME_BIN_PATH
export RENDER=true

echo "Environment variables set:"
echo "CHROME_BIN=$CHROME_BIN"

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROME_VERSION=$($CHROME_BIN_PATH --version | awk '{print $3}' | cut -d'.' -f1)
if [ ! -z "$CHROME_VERSION" ]; then
    CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
    if [ ! -z "$CHROMEDRIVER_VERSION" ]; then
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
        unzip /tmp/chromedriver.zip -d /usr/local/bin/
        chmod +x /usr/local/bin/chromedriver
        rm /tmp/chromedriver.zip
        
        if [ -f "/usr/local/bin/chromedriver" ]; then
            echo "✅ ChromeDriver installed at /usr/local/bin/chromedriver"
            echo "export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver" >> $HOME/.chrome_env
            export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
            echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"
        else
            echo "❌ ChromeDriver installation failed"
        fi
    else
        echo "❌ Could not determine ChromeDriver version"
    fi
else
    echo "❌ Could not determine Chrome version"
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