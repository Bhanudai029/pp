#!/usr/bin/env python3
"""
Install Chrome and ChromeDriver for Render deployment with comprehensive debugging
"""
import os
import subprocess
import sys
import platform
import shutil
from pathlib import Path

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_system_info():
    """Print detailed system information"""
    print_section("SYSTEM INFORMATION")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    
    # Check if we're root (Linux only)
    if platform.system() != "Windows":
        try:
            print(f"\nRunning as UID: {os.getuid()}")
            print(f"Running as GID: {os.getgid()}")
        except AttributeError:
            pass  # Windows doesn't have these functions
    
    print(f"User: {os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))}")
    print(f"Home: {os.environ.get('HOME', os.environ.get('USERPROFILE', 'unknown'))}")
    print(f"PWD: {os.getcwd()}")
    
    # Check available space (Linux only)
    if platform.system() != "Windows":
        try:
            stat = os.statvfs('/')
            free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            print(f"\nFree disk space: {free_space_gb:.2f} GB")
        except AttributeError:
            pass  # Windows doesn't have statvfs
    else:
        print("\nFree disk space: Not available on Windows")

def check_existing_installations():
    """Check for existing Chrome/Chromium installations"""
    print_section("CHECKING EXISTING INSTALLATIONS")
    
    browsers = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/snap/bin/chromium',
        '/usr/local/bin/chrome'
    ]
    
    drivers = [
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver',
        '/opt/chromedriver/chromedriver',
        '/snap/bin/chromedriver'
    ]
    
    print("\nChecking for browsers:")
    for browser in browsers:
        if os.path.exists(browser):
            print(f"  ✓ Found: {browser}")
            try:
                result = subprocess.run([browser, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"    Version: {result.stdout.strip()}")
            except:
                pass
        else:
            print(f"  ✗ Not found: {browser}")
    
    print("\nChecking for drivers:")
    for driver in drivers:
        if os.path.exists(driver):
            print(f"  ✓ Found: {driver}")
            try:
                result = subprocess.run([driver, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"    Version: {result.stdout.strip()}")
            except:
                pass
        else:
            print(f"  ✗ Not found: {driver}")
    
    # Check if chrome is in PATH
    print("\nChecking PATH for chrome:")
    chrome_in_path = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    if chrome_in_path:
        print(f"  ✓ Chrome found in PATH: {chrome_in_path}")
    else:
        print(f"  ✗ Chrome not found in PATH")
    
    chromedriver_in_path = shutil.which('chromedriver')
    if chromedriver_in_path:
        print(f"  ✓ ChromeDriver found in PATH: {chromedriver_in_path}")
    else:
        print(f"  ✗ ChromeDriver not found in PATH")

def run_command(cmd, shell=True, verbose=True):
    """Run a shell command with detailed output"""
    if verbose:
        print(f"\n📍 Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=300)
        
        if verbose:
            if result.stdout:
                print(f"   stdout: {result.stdout[:500]}..." if len(result.stdout) > 500 else f"   stdout: {result.stdout}")
            if result.stderr:
                print(f"   stderr: {result.stderr[:500]}..." if len(result.stderr) > 500 else f"   stderr: {result.stderr}")
            print(f"   Return code: {result.returncode}")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"   ⏱️ Command timed out after 300 seconds")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def create_environment_file():
    """Create environment file with Chrome paths for Render"""
    print_section("CREATING ENVIRONMENT FILE")
    
    env_vars = {
        'CHROME_BIN': '/usr/bin/google-chrome-stable',
        'CHROMEDRIVER_PATH': '/usr/local/bin/chromedriver'
    }
    
    # Create environment file in home directory
    env_file_path = Path.home() / '.chrome_env'
    print(f"Creating environment file at: {env_file_path}")
    
    with open(env_file_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f'export {key}={value}\n')
    
    # Also set environment variables for current session
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("Environment variables set:")
    for key, value in env_vars.items():
        print(f"  {key}={value}")

def main():
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  CHROME INSTALLATION SCRIPT WITH DETAILED DEBUGGING".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    
    # Step 1: System information
    check_system_info()
    
    # Step 2: Check existing installations
    check_existing_installations()
    
    print_section("STARTING INSTALLATION PROCESS")
    
    # Update package list
    print("Updating package list...")
    run_command("apt-get update -qq")
    
    # Install wget and dependencies
    print("Installing dependencies...")
    run_command("apt-get install -y -qq wget gnupg unzip curl")
    
    # Add Google Chrome repository
    print("Adding Google Chrome repository...")
    run_command("wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -")
    run_command('echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list')
    
    # Update package list again
    print("Updating package list with Chrome repository...")
    run_command("apt-get update -qq")
    
    # Install Chrome
    print("Installing Google Chrome...")
    if not run_command("apt-get install -y -qq google-chrome-stable"):
        print("Failed to install Chrome")
        sys.exit(1)
    
    print_section("VERIFYING CHROME INSTALLATION")
    
    # Check if Chrome was installed
    chrome_path = "/usr/bin/google-chrome-stable"
    if os.path.exists(chrome_path):
        print(f"✅ Chrome binary found at: {chrome_path}")
        
        # Get Chrome version
        result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Browser version: {result.stdout.strip()}")
            
            # Extract version for ChromeDriver
            try:
                chrome_version = result.stdout.split()[2].split('.')[0]
                print(f"Browser major version: {chrome_version}")
                
                print_section("INSTALLING CHROMEDRIVER")
                
                # Install ChromeDriver
                chromedriver_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}"
                result = subprocess.run(["curl", "-sS", chromedriver_url], capture_output=True, text=True)
                if result.returncode == 0:
                    chromedriver_version = result.stdout.strip()
                    print(f"Installing ChromeDriver version: {chromedriver_version}")
                    
                    download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_linux64.zip"
                    if run_command(f"wget -O /tmp/chromedriver.zip {download_url}"):
                        run_command("unzip -o /tmp/chromedriver.zip -d /usr/local/bin/")
                        run_command("chmod +x /usr/local/bin/chromedriver")
                        run_command("rm /tmp/chromedriver.zip")
                        
                        if os.path.exists("/usr/local/bin/chromedriver"):
                            print("✅ ChromeDriver installed at /usr/local/bin/chromedriver")
                            result = subprocess.run(["/usr/local/bin/chromedriver", "--version"], capture_output=True, text=True)
                            if result.returncode == 0:
                                print(f"✅ ChromeDriver version: {result.stdout.strip()}")
                                
                                # Create environment file
                                create_environment_file()
                        else:
                            print("❌ ChromeDriver not found at expected location")
                            sys.exit(1)
                    else:
                        print("❌ Failed to download ChromeDriver")
                        sys.exit(1)
                else:
                    print("❌ Failed to get ChromeDriver version")
                    sys.exit(1)
            except Exception as e:
                print(f"Error installing ChromeDriver: {e}")
                sys.exit(1)
        else:
            print("❌ Failed to get Chrome version")
            sys.exit(1)
    else:
        print("❌ Chrome binary not found after installation!")
        print("\nAttempting alternative installation method...")
        
        # Try installing chromium as fallback
        print("\nTrying Chromium installation as fallback...")
        if run_command("apt-get install -y chromium-browser chromium-driver"):
            if os.path.exists("/usr/bin/chromium-browser"):
                print("✅ Chromium installed successfully as fallback")
                # Create symlink for compatibility
                run_command("ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver")
                # Create environment file
                create_environment_file()
            else:
                print("❌ Chromium browser not found")
                sys.exit(1)
        else:
            print("❌ Failed to install any browser!")
            sys.exit(1)
    
    print_section("FINAL VERIFICATION")
    check_existing_installations()
    
    print_section("CREATING TEST SCRIPT")
    
    # Create a test script
    test_script = '''#!/usr/bin/env python3
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("Testing Selenium with Chrome/Chromium...")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Try different Chrome binary locations
for chrome_path in ["/usr/bin/google-chrome-stable", "/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium"]:
    if os.path.exists(chrome_path):
        options.binary_location = chrome_path
        print(f"Using browser: {chrome_path}")
        break

try:
    driver = webdriver.Chrome(options=options)
    print("✅ Selenium WebDriver initialized successfully!")
    driver.quit()
except Exception as e:
    print(f"❌ Failed to initialize WebDriver: {e}")
'''
    
    with open('/tmp/test_selenium.py', 'w') as f:
        f.write(test_script)
    
    print("Created test script at /tmp/test_selenium.py")
    print("You can test it with: python3 /tmp/test_selenium.py")
    
    print("\n" + "=" * 70)
    print("=".center(70))
    print("INSTALLATION COMPLETED".center(70))
    print("=".center(70))
    print("=" * 70)

if __name__ == "__main__":
    main()
