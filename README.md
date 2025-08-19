# Facebook Profile Picture Downloader

This repository contains multiple Python scripts and a JavaScript API for downloading profile pictures from Facebook URLs using different approaches:

## Requirements

- Python 3.6 or higher (for Python scripts)
- Node.js 14+ (for JavaScript API)
- Chrome Browser
- Required Python packages:
  - selenium
  - requests
  - webdriver-manager
  - beautifulsoup4
  - pillow
  - flask
  - flask-cors
- Required Node.js packages (for API):
  - express
  - cors
  - axios
  - puppeteer

## Installation

### Python Scripts
1. Make sure you have Python installed
2. Install the required packages:
   ```
   pip install selenium requests webdriver-manager beautifulsoup4 pillow flask flask-cors
   ```

### JavaScript API
1. Navigate to the `api` directory:
   ```
   cd api
   ```
2. Install the required packages:
   ```
   npm install
   ```

## Usage

### Method 1: Web UI Version (fb_profile_downloader_web.py) - Recommended
This version provides a web interface for downloading Facebook profile pictures without opening file explorer.

1. Start the web server:
   ```bash
   python fb_profile_downloader_web.py
   ```
2. Open your browser and go to http://localhost:5000
3. Enter the Facebook photo URL and click "Download Profile Picture"

### Method 2: UI Version (fb_profile_downloader_ui.py)
This version uses the ESC key technique and provides a graphical interface to view the screenshot.

```bash
python fb_profile_downloader_ui.py "https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887"
```

### Method 3: Simple Headless Version (fb_profile_downloader_simple.py)
This version runs in headless mode and doesn't open file explorer.

```bash
python fb_profile_downloader_simple.py "https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887"
```

### Method 4: Selenium Version (fb_profile_downloader.py)
This version uses browser automation to access the page like a real user.

```bash
python fb_profile_downloader.py "https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887"
```

### Method 5: JavaScript API (api/)
This version provides a REST API for downloading Facebook profile pictures.

1. Navigate to the API directory:
   ```
   cd api
   ```
2. Start the server:
   ```
   npm start
   ```
3. Use the API endpoint:
   ```
   POST /download
   {
     "url": "https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887"
   }
   ```

## How It Works

### Web UI Version (Recommended)
1. Starts a local web server on port 5000
2. Provides a web interface for entering Facebook URLs
3. Uses Selenium in headless mode to download profile pictures
4. Allows downloading the image directly from the browser

### UI Version
1. Takes a Facebook photo URL as input
2. Uses Selenium with Chrome WebDriver to open the URL
3. Automatically presses the ESC key to exit the photo viewer
4. Takes a screenshot of the page showing the profile picture
5. Displays the screenshot in a graphical interface
6. Allows saving the screenshot to a desired location

### Simple Headless Version
1. Takes a Facebook photo URL as input
2. Uses Selenium in headless mode to access the page
3. Automatically presses the ESC key to exit the photo viewer
4. Downloads the image directly
5. Saves the image in a "downloads" folder with the name "Free_FB_Zone_Profile_Picture.png"
6. Provides a download link in the response

### Selenium Version
1. Takes a Facebook photo URL as input
2. Uses Selenium with Chrome WebDriver to open the URL
3. Automatically presses the ESC key to exit the photo viewer
4. Takes a screenshot and saves it to the "downloads" folder

### JavaScript API
1. Provides a REST endpoint for downloading Facebook profile pictures
2. Uses Puppeteer in headless mode to access the page
3. Automatically presses the ESC key to exit the photo viewer
4. Downloads the image directly
5. Saves the image in an "images" folder with the name "Free_FB_Zone_Profile_Picture.png"
6. Returns a download URL in the response

## Note

- Facebook frequently changes its UI and security measures, so these scripts might need updates over time
- Some photos may not be downloadable if they are private or have privacy restrictions
- For best results, make sure you have Chrome browser installed
- The Web UI version provides the best user experience with minimal resource usage

## Troubleshooting WinError 193 on Windows

If you encounter the error "[WinError 193] %1 is not a valid Win32 application":

1. This typically indicates an architecture mismatch between your Python installation and ChromeDriver
2. Check if your Python is 32-bit or 64-bit:
   ```python
   import platform
   print(platform.architecture())
   ```
3. Ensure your Chrome browser matches your Python architecture (both 32-bit or both 64-bit)
4. Try using the Web UI version which has better error handling for Windows:
   ```bash
   python fb_profile_downloader_web.py
   ```
5. As a last resort, manually download ChromeDriver that matches your system architecture from [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)

## Deployment

### Deploying the JavaScript API to Render

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your forked repository
4. Set the build command to `npm install`
5. Set the start command to `npm start`
6. Add the environment variables from `api/.buildpacks`
7. Deploy!

The API will be available at your Render URL.