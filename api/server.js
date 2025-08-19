const express = require('express');
const cors = require('cors');
const axios = require('axios');
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const PORT = process.env.PORT || 10000;

// Middleware
app.use(cors());
app.use(express.json());
app.use('/images', express.static(path.join(__dirname, 'images')));

// Ensure images directory exists
const IMAGES_DIR = path.join(__dirname, 'images');
async function ensureImagesDir() {
  try {
    await fs.access(IMAGES_DIR);
  } catch (error) {
    await fs.mkdir(IMAGES_DIR, { recursive: true });
  }
}

// Function to download Facebook profile picture
async function downloadFacebookProfilePicture(url) {
  let browser;
  try {
    // Launch browser in headless mode
    browser = await puppeteer.launch({
      headless: 'new',
      executablePath: process.env.CHROME_EXECUTABLE_PATH || undefined,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process'
      ]
    });
    
    const page = await browser.newPage();
    
    // Set user agent to avoid detection
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
    
    // Navigate to the Facebook photo URL
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    
    // Wait for page to load
    await page.waitForTimeout(3000);
    
    // Press ESC key to exit photo viewer
    await page.keyboard.press('Escape');
    
    // Wait for page to adjust
    await page.waitForTimeout(2000);
    
    // Find the profile image
    const imgSrc = await page.evaluate(() => {
      // Try multiple selectors for Facebook images
      const selectors = [
        'img[data-visualcompletion="media-vc-image"]',
        'img[src*="fbcdn"]',
        'img[src*="facebook"]'
      ];
      
      for (const selector of selectors) {
        const img = document.querySelector(selector);
        if (img && img.src) {
          return img.src;
        }
      }
      
      // Fallback: get all images and find the largest one
      const images = Array.from(document.querySelectorAll('img'));
      let largestImg = null;
      let largestSize = 0;
      
      for (const img of images) {
        if (img.src && img.src.includes('fbcdn')) {
          // Estimate size based on natural dimensions
          const area = (img.naturalWidth || 0) * (img.naturalHeight || 0);
          if (area > largestSize) {
            largestSize = area;
            largestImg = img.src;
          }
        }
      }
      
      return largestImg;
    });
    
    if (!imgSrc) {
      throw new Error('Could not find profile image on the page');
    }
    
    // Download the image
    const response = await axios({
      method: 'GET',
      url: imgSrc,
      responseType: 'arraybuffer',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    
    // Save with fixed filename
    const filename = 'Free_FB_Zone_Profile_Picture.png';
    const filepath = path.join(IMAGES_DIR, filename);
    
    await fs.writeFile(filepath, response.data);
    
    return filename;
  } catch (error) {
    console.error('Error downloading profile picture:', error);
    throw error;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Routes
app.get('/', (req, res) => {
  res.json({
    message: 'Facebook Profile Picture API',
    endpoints: {
      'POST /download': 'Download a Facebook profile picture'
    }
  });
});

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.post('/download', async (req, res) => {
  try {
    const { url } = req.body;
    
    if (!url) {
      return res.status(400).json({
        success: false,
        error: 'URL is required'
      });
    }
    
    // Basic URL validation
    if (!url.startsWith('https://www.facebook.com/')) {
      return res.status(400).json({
        success: false,
        error: 'Invalid Facebook URL'
      });
    }
    
    // Download the profile picture
    const filename = await downloadFacebookProfilePicture(url);
    
    // Return download URL
    const downloadUrl = `${req.protocol}://${req.get('host')}/images/${filename}`;
    
    res.json({
      success: true,
      downloadUrl: downloadUrl
    });
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to download profile picture'
    });
  }
});

// Initialize and start server
async function startServer() {
  await ensureImagesDir();
  
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Facebook Profile Picture API is running on port ${PORT}`);
    console.log(`Visit http://localhost:${PORT} to test the API`);
  });
}

startServer();