import os
import time
import sys
import requests
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def download_facebook_profile_picture(url, output_dir="downloads"):
    """
    Download a Facebook profile picture from a given URL
    
    Args:
        url (str): The Facebook photo URL
        output_dir (str): Directory to save the downloaded image
    
    Returns:
        str: Path to the downloaded image or None if failed
    """
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # For Windows, specify the executable path explicitly
    if platform.system() == "Windows":
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    driver = None
    try:
        # Initialize the Chrome driver with better error handling
        print("Setting up Chrome driver...")
        # Try to install and setup ChromeDriver with better error handling
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        except Exception as e:
            print(f"Error installing ChromeDriver: {str(e)}")
            # Try alternative approach without webdriver-manager
            print("Trying alternative approach...")
            driver = webdriver.Chrome(options=chrome_options)
        
        # Open the Facebook photo URL
        print(f"Opening URL: {url}")
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(5)
        
        # Try to find the image element
        # Facebook profile images usually have this structure
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        
        profile_img_url = None
        for img in img_elements:
            src = img.get_attribute("src")
            # Look for profile picture URLs (they usually contain specific patterns)
            if src and ("profile" in src.lower() or "photo" in src.lower()) and "fbcdn" in src:
                profile_img_url = src
                break
        
        # If we couldn't find it with the above method, try another approach
        if not profile_img_url:
            # Try to find the main image in a photo view
            img_elements = driver.find_elements(By.CSS_SELECTOR, "img[class*='img'], img[src*='fbcdn']")
            for img in img_elements:
                src = img.get_attribute("src")
                if src and "fbcdn" in src:
                    profile_img_url = src
                    break
        
        if profile_img_url:
            print(f"Found image URL: {profile_img_url}")
            
            # Download the image
            response = requests.get(profile_img_url)
            if response.status_code == 200:
                # Extract filename from URL or create a default one
                filename = profile_img_url.split("/")[-1].split("?")[0]
                if not filename:
                    filename = "profile_picture.jpg"
                
                filepath = os.path.join(output_dir, filename)
                
                # Save the image
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                print(f"Profile picture downloaded successfully: {filepath}")
                return filepath
            else:
                print(f"Failed to download image. Status code: {response.status_code}")
                return None
        else:
            print("Could not find profile image on the page")
            # Take a screenshot for debugging
            screenshot_path = os.path.join(output_dir, "debug_screenshot.png")
            driver.save_screenshot(screenshot_path)
            print(f"Saved page screenshot for debugging: {screenshot_path}")
            return None
            
    except WebDriverException as e:
        print(f"WebDriver error: {str(e)}")
        print("This might be because Chrome/Chromedriver is not properly installed.")
        print("Please make sure you have Chrome browser installed on your system.")
        # Check if it's an architecture mismatch issue
        if "WinError 193" in str(e):
            print("This error often occurs due to architecture mismatch between Python and ChromeDriver.")
            print("Please ensure both Python and Chrome are either 32-bit or 64-bit versions.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Check if it's an architecture mismatch issue
        if "WinError 193" in str(e):
            print("This error often occurs due to architecture mismatch between Python and ChromeDriver.")
            print("Please ensure both Python and Chrome are either 32-bit or 64-bit versions.")
        return None
    finally:
        # Close the driver
        if driver:
            driver.quit()

def main():
    # Get URL from command line argument
    if len(sys.argv) < 2:
        print("Usage: python fb_profile_downloader.py <facebook_photo_url>")
        print("Example: python fb_profile_downloader.py \"https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887\"")
        return
    
    url = sys.argv[1].strip()
    
    if not url:
        print("No URL provided!")
        return
    
    # Validate URL format (basic check)
    if not url.startswith("https://www.facebook.com/"):
        print("Warning: This doesn't look like a Facebook URL, but continuing anyway...")
    
    print("Downloading profile picture...")
    result = download_facebook_profile_picture(url)
    
    if result:
        print(f"Success! Image saved to: {result}")
    else:
        print("Failed to download profile picture.")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have Chrome browser installed")
        print("2. Check your internet connection")
        print("3. The photo might be private or unavailable")
        print("4. Facebook might have changed their page structure")
        print("5. If you're getting a 'WinError 193' message, there might be an architecture mismatch")
        print("   between your Python installation and ChromeDriver. Try:")
        print("   - Check if your Python is 32-bit or 64-bit and ensure Chrome matches")
        print("   - Try running the UI version: python fb_profile_downloader_ui.py <url>")
        print("   - Or try the simple version: python fb_profile_downloader_simple.py <url>")

if __name__ == "__main__":
    main()