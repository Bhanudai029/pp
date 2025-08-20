#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status.
set -e

# Print commands and their arguments as they are executed.
set -x

# Update and install dependencies
echo "Updating package list and installing dependencies..."
apt-get update -y
apt-get install -y wget gnupg unzip curl ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils

# Add Google Chrome repository
echo "Adding Google Chrome repository..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome
echo "Installing Google Chrome..."
apt-get update -y
apt-get install -y google-chrome-stable

# Verify Chrome installation
echo "Verifying Chrome installation..."
google-chrome-stable --version

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Verify ChromeDriver installation
echo "Verifying ChromeDriver installation..."
chromedriver --version

# Set environment variables in .env file
echo "Creating .env file..."
echo "CHROME_BIN=/usr/bin/google-chrome-stable" > .env
echo "CHROMEDRIVER_PATH=/usr/local/bin/chromedriver" >> .env

# Verify that the binaries are executable
echo "Verifying binaries..."
if [ ! -x "/usr/bin/google-chrome-stable" ]; then
  echo "Error: Chrome binary not found or not executable at /usr/bin/google-chrome-stable"
  exit 1
fi

if [ ! -x "/usr/local/bin/chromedriver" ]; then
  echo "Error: ChromeDriver binary not found or not executable at /usr/local/bin/chromedriver"
  exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create and set permissions for the downloads directory
echo "Creating downloads directory..."
mkdir -p downloads
chmod 777 downloads

echo "Build script finished successfully."
