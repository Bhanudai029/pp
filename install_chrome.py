#!/usr/bin/env python3
"""
Install Chrome and ChromeDriver for Render deployment
"""
import os
import subprocess
import sys

def run_command(cmd, shell=True):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running: {cmd}")
            print(f"stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception running {cmd}: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("Installing Chrome for Render")
    print("=" * 50)
    
    # Update package list
    print("Updating package list...")
    run_command("apt-get update -qq")
    
    # Install wget and dependencies
    print("Installing dependencies...")
    run_command("apt-get install -y -qq wget gnupg unzip curl")
    
    # Download Chrome .deb package directly
    print("Downloading Chrome...")
    if not run_command("wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"):
        print("Failed to download Chrome")
        sys.exit(1)
    
    # Install Chrome and its dependencies
    print("Installing Chrome...")
    # First attempt
    if not run_command("apt-get install -y -qq /tmp/chrome.deb"):
        print("First install attempt failed, trying to fix dependencies...")
        run_command("apt-get update -qq")
        run_command("apt-get install -f -y -qq")
        # Second attempt
        if not run_command("apt-get install -y -qq /tmp/chrome.deb"):
            print("Chrome installation failed!")
            sys.exit(1)
    
    # Clean up
    run_command("rm /tmp/chrome.deb")
    
    # Verify Chrome installation
    print("\nVerifying Chrome installation...")
    if os.path.exists("/usr/bin/google-chrome-stable"):
        print("✓ Chrome binary found at /usr/bin/google-chrome-stable")
        result = subprocess.run(["google-chrome-stable", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Chrome version: {result.stdout.strip()}")
            
            # Extract version for ChromeDriver
            chrome_version = result.stdout.split()[2].split('.')[0]
            print(f"Chrome major version: {chrome_version}")
            
            # Install ChromeDriver
            print("\nInstalling ChromeDriver...")
            chromedriver_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}"
            result = subprocess.run(["curl", "-sS", chromedriver_url], capture_output=True, text=True)
            if result.returncode == 0:
                chromedriver_version = result.stdout.strip()
                print(f"Installing ChromeDriver version: {chromedriver_version}")
                
                download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_linux64.zip"
                if run_command(f"wget -q -O /tmp/chromedriver.zip {download_url}"):
                    run_command("unzip -q /tmp/chromedriver.zip -d /usr/local/bin/")
                    run_command("chmod +x /usr/local/bin/chromedriver")
                    run_command("rm /tmp/chromedriver.zip")
                    
                    if os.path.exists("/usr/local/bin/chromedriver"):
                        print("✓ ChromeDriver installed at /usr/local/bin/chromedriver")
                        result = subprocess.run(["/usr/local/bin/chromedriver", "--version"], capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"✓ ChromeDriver version: {result.stdout.strip()}")
                    else:
                        print("✗ ChromeDriver installation failed")
            else:
                print(f"Failed to get ChromeDriver version for Chrome {chrome_version}")
    else:
        print("✗ Chrome binary not found!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Chrome installation completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
