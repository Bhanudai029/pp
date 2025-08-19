import os
import sys
import requests
import subprocess
import platform
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
import time

def download_facebook_profile_picture_simple(url, output_dir="downloads"):
    """
    Download a Facebook profile picture using Selenium and open the downloads folder.
    
    Args:
        url (str): The Facebook photo URL.
        output_dir (str): Directory to save the downloaded image.
    
    Returns:
        str: Path to the downloaded image or None if failed.
    """
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Set up Chrome options
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
                filename = "profile_picture.jpg"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(img_response.content)
                
                absolute_filepath = os.path.abspath(filepath)
                print(f"\n--- DOWNLOAD COMPLETE ---")
                print(f"Image saved successfully to: {absolute_filepath}")
                
                # Open the downloads folder
                print("Opening the downloads folder...")
                subprocess.run(["explorer", os.path.abspath(output_dir)])
                
                return absolute_filepath
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
            print("Please ensure both Python and Chrome are either 32-bit or 64-bit versions.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if "WinError 193" in str(e):
            print("This error often occurs due to architecture mismatch between Python and ChromeDriver.")
            print("Please ensure both Python and Chrome are either 32-bit or 64-bit versions.")
        return None
    finally:
        if driver:
            driver.quit()

def main():
    if len(sys.argv) < 2:
        print("Usage: python fb_profile_downloader_simple.py <facebook_photo_url>")
        print('Example: python fb_profile_downloader_simple.py "https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887"')
        return
    
    url = sys.argv[1].strip()
    
    if not url:
        print("No URL provided!")
        return
    
    print("Downloading profile picture in headless mode...")
    result = download_facebook_profile_picture_simple(url)
    
    if result:
        print(f"\nSuccess! Final image location: {result}")
    else:
        print("\nDownload failed. Please check the errors above.")

if __name__ == "__main__":
    main()
