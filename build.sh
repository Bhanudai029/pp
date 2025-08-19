#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Update package list and install wget
apt-get update
apt-get install -y wget gnupg

# Add Google Chrome's official repository
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Update package list
apt-get update

# Install dependencies for Chrome
apt-get install -y \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libdrm2 \
    libgbm1 \
    libxshmfence1 \
    fonts-liberation \
    libappindicator1 \
    xdg-utils

# Install Google Chrome
echo "Installing Google Chrome..."
apt-get install -y google-chrome-stable

# Verify Chrome installation
echo "Chrome installed at:"
which google-chrome-stable
google-chrome-stable --version || echo "Chrome version check failed"

# Get Chrome version for ChromeDriver
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | cut -d'.' -f1)
echo "Chrome major version: $CHROME_VERSION"

# Install ChromeDriver
echo "Installing ChromeDriver..."
# Get the latest ChromeDriver version that matches Chrome version
CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download and install ChromeDriver
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Verify ChromeDriver installation
echo "ChromeDriver installed at:"
which chromedriver
/usr/local/bin/chromedriver --version || echo "ChromeDriver version check failed"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create downloads directory
mkdir -p downloads
chmod 777 downloads

echo "Build completed successfully!"
echo "Chrome binary: $(which google-chrome-stable)"
echo "ChromeDriver binary: $(which chromedriver)"
