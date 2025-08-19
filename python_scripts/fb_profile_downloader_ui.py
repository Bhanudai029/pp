import os
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from PIL import Image, ImageTk

class FacebookProfileDownloader:
    def __init__(self):
        self.driver = None
        self.screenshot_path = None
        self.root = None
        self.image_label = None
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # Remove headless mode so we can see what's happening
        # chrome_options.add_argument("--headless")
        
        try:
            # Try to find Chrome executable
            chrome_paths = [
                "C:/Program Files/Google/Chrome/Application/chrome.exe",
                "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
                "C:/Users/%USERNAME%/AppData/Local/Google/Chrome/Application/chrome.exe"
            ]
            
            chrome_executable = None
            for path in chrome_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    chrome_executable = expanded_path
                    break
            
            if chrome_executable:
                chrome_options.binary_location = chrome_executable
                print(f"Found Chrome at: {chrome_executable}")
            
            # Try to initialize the driver without webdriver-manager
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"Error setting up Chrome driver: {str(e)}")
            print("Make sure you have Chrome browser installed on your system.")
            return False
    
    def download_profile_picture(self, url):
        """Download Facebook profile picture using the ESC method"""
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            # Open the Facebook photo URL
            print(f"Opening URL: {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Press ESC key to exit photo viewer
            print("Pressing ESC key...")
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            
            # Wait a moment for the page to adjust
            time.sleep(2)
            
            # Take a screenshot
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
                
            self.screenshot_path = os.path.join("downloads", "facebook_profile_screenshot.png")
            self.driver.save_screenshot(self.screenshot_path)
            print(f"Screenshot saved: {self.screenshot_path}")
            return True
            
        except Exception as e:
            print(f"Error during download: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up the driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def show_screenshot_ui(self):
        """Show the screenshot in a UI window"""
        if not self.screenshot_path or not os.path.exists(self.screenshot_path):
            print("No screenshot available to display")
            return
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Facebook Profile Picture Downloader")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Facebook Profile Picture", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Screenshot display
        screenshot_frame = ttk.LabelFrame(main_frame, text="Profile Screenshot", padding="10")
        screenshot_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Load and display image
        self.display_screenshot(screenshot_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        save_button = ttk.Button(button_frame, text="Save Screenshot", command=self.save_screenshot)
        save_button.grid(row=0, column=0, padx=(0, 10))
        
        close_button = ttk.Button(button_frame, text="Close", command=self.root.destroy)
        close_button.grid(row=0, column=1)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        screenshot_frame.columnconfigure(0, weight=1)
        screenshot_frame.rowconfigure(0, weight=1)
        
        # Start the UI
        self.root.mainloop()
    
    def display_screenshot(self, parent):
        """Display the screenshot in the UI"""
        # Load and resize image
        image = Image.open(self.screenshot_path)
        
        # Resize to fit in the window while maintaining aspect ratio
        max_width = 700
        max_height = 400
        
        image.thumbnail((max_width, max_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Create label to display image
        if self.image_label is None:
            self.image_label = ttk.Label(parent, image=photo)
            self.image_label.image = photo  # Keep a reference
            self.image_label.grid(row=0, column=0)
        else:
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Keep a reference
    
    def save_screenshot(self):
        """Save the screenshot to a user-selected location"""
        if not self.screenshot_path or not os.path.exists(self.screenshot_path):
            messagebox.showerror("Error", "No screenshot available to save")
            return
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Screenshot As"
        )
        
        if file_path:
            try:
                # Copy the file
                from shutil import copyfile
                copyfile(self.screenshot_path, file_path)
                messagebox.showinfo("Success", f"Screenshot saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save screenshot:\n{str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python fb_profile_downloader_ui.py <facebook_photo_url>")
        print("Example: python fb_profile_downloader_ui.py \"https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887\"")
        return
    
    url = sys.argv[1].strip()
    
    if not url:
        print("No URL provided!")
        return
    
    # Create downloader instance
    downloader = FacebookProfileDownloader()
    
    try:
        # Download the profile picture
        print("Downloading profile picture...")
        success = downloader.download_profile_picture(url)
        
        if success:
            print("Opening UI to display screenshot...")
            downloader.show_screenshot_ui()
        else:
            print("Failed to download profile picture.")
    finally:
        downloader.cleanup()

if __name__ == "__main__":
    main()