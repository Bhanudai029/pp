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

app = Flask(__name__)
CORS(app)

# Configure downloads directory
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

# Global variable to store the last downloaded file path
last_downloaded_file = None

def download_facebook_profile_picture(url):
    """
    Download a Facebook profile picture using Selenium in headless mode.
    
    Args:
        url (str): The Facebook photo URL.
    
    Returns:
        str: Path to the downloaded image or None if failed.
    """
    
    # Set up Chrome options for headless operation
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # For Windows, specify the executable path explicitly
    if platform.system() == "Windows":
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    driver = None
    try:
        # Try to install and setup ChromeDriver with better error handling
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        except Exception as e:
            print(f"Error installing ChromeDriver: {str(e)}")
            # Try alternative approach without webdriver-manager
            print("Trying alternative approach...")
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.set_page_load_timeout(30)
        
        print(f"Opening URL: {url}")
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
            print(f"Primary image selector failed. {e}")

        if profile_img_url:
            print(f"Downloading image from: {profile_img_url}")
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
                print(f"ERROR: Failed to download image. Status code: {img_response.status_code}")
                return None
        else:
            print("ERROR: Could not find profile image URL.")
            return None
            
    except WebDriverException as e:
        print(f"WebDriver error: {str(e)}")
        if "WinError 193" in str(e):
            print("This error often occurs due to architecture mismatch between Python and ChromeDriver.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if "WinError 193" in str(e):
            print("This error often occurs due to architecture mismatch between Python and ChromeDriver.")
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
        
        # Validate URL format (basic check)
        if not url.startswith("https://www.facebook.com/"):
            # We'll still try to process it but warn the user
            pass
        
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
        return jsonify({'success': False, 'error': f'Error serving file: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Facebook Profile Picture Downloader Web Server...")
    print("Open your browser and go to http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)