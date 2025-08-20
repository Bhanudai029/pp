import os
import sys
import time
import platform
import requests
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, request, render_template, send_file, jsonify
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure downloads directory
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

# Global variable to store the last downloaded file path
last_downloaded_file = None

def get_chrome_options():
    """Get Chrome options configured for Render environment"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Try multiple Chrome binary locations
    chrome_locations = [
        os.environ.get("CHROME_BIN"),
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/opt/google/chrome/google-chrome"
    ]
    
    chrome_found = False
    for chrome_path in chrome_locations:
        if chrome_path and os.path.exists(chrome_path):
            chrome_options.binary_location = chrome_path
            logger.info(f"Chrome binary found at: {chrome_path}")
            chrome_found = True
            break
    
    if not chrome_found:
        logger.error("Chrome binary not found in any expected location!")
        logger.error(f"Searched locations: {chrome_locations}")
        raise FileNotFoundError("Chrome browser is not installed. Please ensure Chrome is installed via build.sh")
    
    return chrome_options

def get_chrome_driver():
    """Get Chrome driver configured for the environment"""
    try:
        chrome_options = get_chrome_options()
    except FileNotFoundError as e:
        logger.error(str(e))
        raise
    
    # Try multiple ChromeDriver locations
    chromedriver_locations = [
        os.environ.get("CHROMEDRIVER_PATH"),
        "/usr/local/bin/chromedriver",
        "/usr/bin/chromedriver",
        "/opt/chromedriver/chromedriver"
    ]
    
    for chromedriver_path in chromedriver_locations:
        if chromedriver_path and os.path.exists(chromedriver_path):
            try:
                logger.info(f"Attempting to use ChromeDriver at: {chromedriver_path}")
                service = Service(chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info(f"Successfully initialized ChromeDriver from: {chromedriver_path}")
                return driver
            except Exception as e:
                logger.warning(f"Failed to use ChromeDriver at {chromedriver_path}: {str(e)}")
                continue
    
    # If we're not on Render (local development), try webdriver-manager
    if not os.environ.get("RENDER"):
        logger.info("Attempting to use webdriver-manager for ChromeDriver (local development)")
        try:
            # Disable WDM logging to avoid confusion
            os.environ['WDM_LOG'] = '0'
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver installed at: {driver_path}")
            return webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        except Exception as e:
            logger.error(f"Error with webdriver-manager: {str(e)}")
    
    # If all else fails, try without explicit service (might work with PATH)
    try:
        logger.info("Last attempt: Trying to use Chrome without explicit driver path")
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Successfully initialized ChromeDriver without explicit path")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize ChromeDriver: {str(e)}")
        raise RuntimeError("Unable to initialize ChromeDriver. Please ensure Chrome and ChromeDriver are properly installed.")

def download_facebook_profile_picture(url):
    """
    Download a Facebook profile picture using Selenium in headless mode.
    
    Args:
        url (str): The Facebook photo URL.
    
    Returns:
        str: Path to the downloaded image or None if failed.
    """
    
    driver = None
    try:
        driver = get_chrome_driver()
        driver.set_page_load_timeout(30)
        
        logger.info(f"Opening URL: {url}")
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(2)
        
        # Press ESC key to exit photo viewer
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        
        # Wait a moment for the page to adjust
        time.sleep(2)

        profile_img_url = None
        try:
            # Wait for image element
            wait = WebDriverWait(driver, 10)
            img_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//img[@data-visualcompletion='media-vc-image'] | //img[contains(@class, 'i09qtzwb')] ")))
            profile_img_url = img_element.get_attribute('src')

        except Exception as e:
            logger.warning(f"Primary image selector failed. {e}")

        if profile_img_url:
            logger.info(f"Downloading image from: {profile_img_url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            img_response = requests.get(profile_img_url, headers=headers)
            
            if img_response.status_code == 200:
                # Use a fixed filename as requested
                filename = "Free_FB_Zone_Profile_Picture.png"
                filepath = os.path.join(DOWNLOADS_DIR, filename)
                
                with open(filepath, "wb") as f:
                    f.write(img_response.content)
                
                return filepath
            else:
                logger.error(f"Failed to download image. Status code: {img_response.status_code}")
                return None
        else:
            logger.error("Could not find profile image URL.")
            return None
            
    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
    finally:
        if driver:
            driver.quit()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Facebook Profile Picture Downloader</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #3b5998;
                text-align: center;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input[type="url"] {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            button {
                background-color: #3b5998;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            button:hover {
                background-color: #2d4373;
            }
            button:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
            }
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 5px;
                display: none;
            }
            .success {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }
            .error {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }
            .loading {
                text-align: center;
                display: none;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3b5998;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Facebook Profile Picture Downloader</h1>
            <form id="downloadForm">
                <div class="form-group">
                    <label for="url">Facebook Photo URL:</label>
                    <input type="url" id="url" name="url" required placeholder="https://www.facebook.com/photo/?fbid=...">
                </div>
                <button type="submit" id="downloadBtn">Download Profile Picture</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Downloading profile picture... This may take a few seconds.</p>
            </div>
            
            <div class="result" id="result"></div>
        </div>

        <script>
            document.getElementById('downloadForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const url = document.getElementById('url').value;
                const downloadBtn = document.getElementById('downloadBtn');
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                
                // Disable button and show loading
                downloadBtn.disabled = true;
                loading.style.display = 'block';
                result.style.display = 'none';
                
                // Send request to server
                fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({url: url})
                })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';
                    if (data.success) {
                        result.className = 'result success';
                        result.innerHTML = `
                            <h3>Download Successful!</h3>
                            <p>Profile picture downloaded successfully.</p>
                            <button onclick="downloadImage()" style="margin-top: 10px; padding: 10px 15px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">Download Image</button>
                        `;
                    } else {
                        result.className = 'result error';
                        result.innerHTML = `<h3>Download Failed</h3><p>${data.error}</p>`;
                    }
                    result.style.display = 'block';
                })
                .catch(error => {
                    loading.style.display = 'none';
                    result.className = 'result error';
                    result.innerHTML = `<h3>Error</h3><p>An unexpected error occurred: ${error.message}</p>`;
                    result.style.display = 'block';
                })
                .finally(() => {
                    downloadBtn.disabled = false;
                });
            });
            
            function downloadImage() {
                // Create a temporary link and trigger download
                const link = document.createElement('a');
                link.href = '/download_file';
                link.download = 'Free_FB_Zone_Profile_Picture.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        </script>
    </body>
    </html>
    '''

@app.route('/download', methods=['POST'])
def download():
    global last_downloaded_file
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400
        
        # Download the profile picture
        filepath = download_facebook_profile_picture(url)
        
        if filepath and os.path.exists(filepath):
            # Store the file path for later download
            last_downloaded_file = filepath
            return jsonify({
                'success': True
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to download profile picture. The photo might be private or unavailable.'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in download endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/download_file')
def download_file():
    global last_downloaded_file
    try:
        # Check if we have a downloaded file
        if last_downloaded_file and os.path.exists(last_downloaded_file):
            return send_file(
                last_downloaded_file, 
                as_attachment=True, 
                download_name="Free_FB_Zone_Profile_Picture.png",
                mimetype='image/png'
            )
        else:
            return jsonify({'success': False, 'error': 'No file available for download'}), 404
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return jsonify({'success': False, 'error': f'Error serving file: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/debug')
def debug():
    """Comprehensive debug endpoint with extensive diagnostics"""
    import subprocess
    import platform as plat
    import shutil
    import glob
    
    debug_info = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'system': {
            'platform': plat.platform(),
            'system': plat.system(),
            'release': plat.release(),
            'version': plat.version(),
            'machine': plat.machine(),
            'processor': plat.processor(),
            'python_version': sys.version
        },
        'environment': {
            'CHROME_BIN': os.environ.get('CHROME_BIN', 'Not set'),
            'CHROMEDRIVER_PATH': os.environ.get('CHROMEDRIVER_PATH', 'Not set'),
            'PORT': os.environ.get('PORT', 'Not set'),
            'PATH': os.environ.get('PATH', 'Not set'),
            'USER': os.environ.get('USER', 'Not set'),
            'HOME': os.environ.get('HOME', 'Not set'),
            'PWD': os.getcwd()
        },
        'chrome_paths': {},
        'processes': {}
    }
    
    # Check various Chrome paths with detailed info
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/snap/bin/chromium'
    ]
    
    debug_info['browsers'] = {}
    for path in chrome_paths:
        if os.path.exists(path):
            debug_info['browsers'][path] = {
                'exists': True,
                'size': os.path.getsize(path),
                'executable': os.access(path, os.X_OK)
            }
            try:
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    debug_info['browsers'][path]['version'] = result.stdout.strip()
                else:
                    debug_info['browsers'][path]['version'] = f"Error: {result.stderr}"
            except Exception as e:
                debug_info['browsers'][path]['version'] = f"Exception: {str(e)}"
        else:
            debug_info['browsers'][path] = {'exists': False}
    
    # Check ChromeDriver paths with detailed info
    chromedriver_paths = [
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver',
        '/opt/chromedriver/chromedriver'
    ]
    
    debug_info['drivers'] = {}
    for path in chromedriver_paths:
        if os.path.exists(path):
            debug_info['drivers'][path] = {
                'exists': True,
                'size': os.path.getsize(path),
                'executable': os.access(path, os.X_OK)
            }
            try:
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    debug_info['drivers'][path]['version'] = result.stdout.strip()
                else:
                    debug_info['drivers'][path]['version'] = f"Error: {result.stderr}"
            except Exception as e:
                debug_info['drivers'][path]['version'] = f"Exception: {str(e)}"
        else:
            debug_info['drivers'][path] = {'exists': False}
    
    # Check PATH for executables
    debug_info['in_path'] = {
        'chrome': shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        'chromium': shutil.which('chromium') or shutil.which('chromium-browser'),
        'chromedriver': shutil.which('chromedriver')
    }
    
    # List all files in /usr/bin that contain 'chrome' or 'chromium'
    debug_info['chrome_related_files'] = []
    try:
        for file in glob.glob('/usr/bin/*chrome*') + glob.glob('/usr/bin/*chromium*'):
            debug_info['chrome_related_files'].append(file)
    except:
        pass
    
    # Check running processes
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            chrome_processes = [line for line in result.stdout.split('\n') if 'chrome' in line.lower()]
            debug_info['processes']['chrome_running'] = len(chrome_processes) > 0
            debug_info['processes']['count'] = len(chrome_processes)
            if chrome_processes:
                debug_info['processes']['samples'] = chrome_processes[:3]  # Show first 3
    except:
        debug_info['processes']['error'] = 'Could not check processes'
    
    # Test Selenium initialization
    debug_info['selenium_test'] = {}
    try:
        test_options = Options()
        test_options.add_argument('--headless')
        test_options.add_argument('--no-sandbox')
        test_options.add_argument('--disable-dev-shm-usage')
        
        # Find available browser
        browser_found = None
        for browser_path in ['/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/usr/bin/chromium-browser', '/usr/bin/chromium']:
            if os.path.exists(browser_path):
                browser_found = browser_path
                test_options.binary_location = browser_path
                break
        
        debug_info['selenium_test']['browser_path'] = browser_found
        
        if browser_found:
            # Try to create driver
            try:
                # Try with explicit chromedriver path
                if os.path.exists('/usr/local/bin/chromedriver'):
                    service = Service('/usr/local/bin/chromedriver')
                    driver = webdriver.Chrome(service=service, options=test_options)
                    debug_info['selenium_test']['initialization'] = 'Success with /usr/local/bin/chromedriver'
                    driver.quit()
                elif os.path.exists('/usr/bin/chromedriver'):
                    service = Service('/usr/bin/chromedriver')
                    driver = webdriver.Chrome(service=service, options=test_options)
                    debug_info['selenium_test']['initialization'] = 'Success with /usr/bin/chromedriver'
                    driver.quit()
                else:
                    driver = webdriver.Chrome(options=test_options)
                    debug_info['selenium_test']['initialization'] = 'Success with default chromedriver'
                    driver.quit()
            except Exception as e:
                debug_info['selenium_test']['initialization'] = f'Failed: {str(e)}'
        else:
            debug_info['selenium_test']['initialization'] = 'No browser found'
    except Exception as e:
        debug_info['selenium_test']['error'] = str(e)
    
    # Disk space check
    try:
        stat = os.statvfs('/')
        debug_info['disk_space'] = {
            'free_gb': (stat.f_bavail * stat.f_frsize) / (1024**3),
            'total_gb': (stat.f_blocks * stat.f_frsize) / (1024**3)
        }
    except:
        debug_info['disk_space'] = 'Could not check'
    
    # Memory info
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemTotal' in line:
                    debug_info['memory_total'] = line
                elif 'MemAvailable' in line:
                    debug_info['memory_available'] = line
    except:
        debug_info['memory'] = 'Could not check'
    
    return jsonify(debug_info), 200

if __name__ == '__main__':
    # Use PORT from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    # In production, Gunicorn will handle this, but this is for local testing
    app.run(host='0.0.0.0', port=port, debug=False)
