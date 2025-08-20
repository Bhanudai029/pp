#!/usr/bin/env bash
# exit on error
set -o errexit

echo "========================================"
echo "Starting build process for Render"
echo "========================================"

# Update package lists
echo "Updating package lists..."
apt-get update

# Install wget and curl if not present
apt-get install -y wget curl

# Install dependencies for Chrome
echo "Installing Chrome dependencies..."
apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    libglib2.0-0

# Download and install Google Chrome Stable
echo "Installing Google Chrome..."
wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y /tmp/google-chrome-stable_current_amd64.deb
rm /tmp/google-chrome-stable_current_amd64.deb

# Verify Chrome installation
echo "Chrome installed at: $(which google-chrome-stable)"
echo "Chrome version: $(google-chrome-stable --version)"

# Get Chrome major version for ChromeDriver compatibility
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | awk -F'.' '{print $1}')
echo "Chrome major version: $CHROME_VERSION"

# Install ChromeDriver using the new Chrome for Testing API
echo "Installing ChromeDriver..."

# Get the latest ChromeDriver version that matches our Chrome major version
if [ "$CHROME_VERSION" -ge "115" ]; then
    # For Chrome 115+, use the new Chrome for Testing API
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}")
    echo "ChromeDriver version to install: $CHROMEDRIVER_VERSION"
    
    # Download ChromeDriver
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip
    apt-get install -y unzip
    unzip -o /tmp/chromedriver.zip -d /tmp/
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
    chmod +x /usr/local/bin/chromedriver
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64
else
    # For older Chrome versions, use the traditional ChromeDriver API
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
    echo "ChromeDriver version to install: $CHROMEDRIVER_VERSION"
    
    wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" -O /tmp/chromedriver.zip
    apt-get install -y unzip
    unzip -o /tmp/chromedriver.zip -d /tmp/
    mv /tmp/chromedriver /usr/local/bin/chromedriver
    chmod +x /usr/local/bin/chromedriver
    rm /tmp/chromedriver.zip
fi

# Verify ChromeDriver installation
echo "ChromeDriver installed at: $(which chromedriver)"
echo "ChromeDriver version: $(chromedriver --version)"

# Set environment variables
export CHROME_BIN=/usr/bin/google-chrome-stable
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

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
