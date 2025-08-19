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
    chrome_options.add_argument("--headless")
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
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Use Chrome binary from environment variable if available
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin and os.path.exists(chrome_bin):
        chrome_options.binary_location = chrome_bin
        logger.info(f"Using Chrome binary from CHROME_BIN: {chrome_bin}")
    elif os.path.exists("/usr/bin/google-chrome-stable"):
        chrome_options.binary_location = "/usr/bin/google-chrome-stable"
        logger.info("Using Chrome binary: /usr/bin/google-chrome-stable")
    elif os.path.exists("/usr/bin/google-chrome"):
        chrome_options.binary_location = "/usr/bin/google-chrome"
        logger.info("Using Chrome binary: /usr/bin/google-chrome")
    else:
        logger.warning("Chrome binary not found in expected locations")
    
    return chrome_options

def get_chrome_driver():
    """Get Chrome driver configured for the environment"""
    chrome_options = get_chrome_options()
    
    # Check if we're on Render (has CHROMEDRIVER_PATH env var)
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    
    if chromedriver_path and os.path.exists(chromedriver_path):
        # Use the ChromeDriver installed by build.sh on Render
        logger.info(f"Using ChromeDriver from CHROMEDRIVER_PATH: {chromedriver_path}")
        service = Service(chromedriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)
    elif os.path.exists("/usr/local/bin/chromedriver"):
        # Try the default installation path
        logger.info("Using ChromeDriver from /usr/local/bin/chromedriver")
        service = Service("/usr/local/bin/chromedriver")
        return webdriver.Chrome(service=service, options=chrome_options)
    else:
        # Use webdriver-manager for local development
        logger.info("Attempting to use webdriver-manager for ChromeDriver")
        try:
            # Disable WDM logging to avoid confusion
            os.environ['WDM_LOG'] = '0'
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver installed at: {driver_path}")
            return webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        except Exception as e:
            logger.error(f"Error with webdriver-manager: {str(e)}")
            # Last resort - try without service
            logger.info("Attempting to use Chrome without explicit driver path")
            return webdriver.Chrome(options=chrome_options)

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

if __name__ == '__main__':
    # Use PORT from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    # In production, Gunicorn will handle this, but this is for local testing
    app.run(host='0.0.0.0', port=port, debug=False)
