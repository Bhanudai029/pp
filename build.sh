#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render
if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src # Make sure we return to where we were
else
  echo "...Using Chrome from cache"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create and set permissions for the downloads directory
echo "Creating downloads directory..."
mkdir -p downloads
chmod 777 downloads

echo "Build script finished successfully."