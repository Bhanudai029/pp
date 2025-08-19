# Facebook Profile Picture Downloader

A Flask web application that allows users to download Facebook profile pictures using Selenium WebDriver.

## Features

- Web interface for easy profile picture downloads
- Headless Chrome browser automation
- Automatic image extraction and download
- Production-ready deployment configuration for Render.com

## Local Development

### Prerequisites

- Python 3.8+
- Google Chrome browser
- Git

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd "api 3 profile pic"
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Deployment to Render.com

### Prerequisites

1. Create a [Render.com](https://render.com) account
2. Push your code to a GitHub repository

### Deployment Steps

1. **Connect GitHub to Render:**
   - Log in to your Render dashboard
   - Click "New +" and select "Web Service"
   - Connect your GitHub account if not already connected
   - Select your repository

2. **Configure the Service:**
   - The service will automatically detect the `render.yaml` file
   - All configuration is already set up in the file
   - The free tier is configured by default

3. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically:
     - Install Chrome and ChromeDriver
     - Install Python dependencies
     - Start the Flask application with Gunicorn

4. **Environment Variables (Optional):**
   If you need to add any custom environment variables:
   - Go to your service dashboard
   - Navigate to "Environment" tab
   - Add your variables

### Files Structure

```
api 3 profile pic/
├── app.py                 # Production-ready Flask application
├── fb_profile_downloader_web.py  # Original web version
├── fb_profile_downloader.py      # CLI version
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment configuration
├── build.sh             # Build script for Chrome installation
├── start.sh             # Start script for Gunicorn
├── .gitignore           # Git ignore file
└── README.md            # This file
```

### Important Files for Deployment

- **`render.yaml`**: Defines the service configuration for Render
- **`build.sh`**: Installs Chrome and ChromeDriver in the Render environment
- **`start.sh`**: Starts the application using Gunicorn
- **`app.py`**: The main application file optimized for production

### Monitoring

Once deployed, you can monitor your application:
- Check logs in the Render dashboard
- Use the `/health` endpoint for health checks
- Monitor the main page at your Render URL

### Troubleshooting

1. **Chrome/ChromeDriver Issues:**
   - The build script automatically installs compatible versions
   - Check logs for any installation errors

2. **Memory Issues:**
   - The free tier has limited memory
   - The app is configured with 2 workers to balance performance and memory

3. **Timeout Issues:**
   - Gunicorn is configured with a 120-second timeout
   - This should be sufficient for most downloads

## API Endpoints

- `GET /` - Main web interface
- `POST /download` - Download profile picture (JSON API)
- `GET /download_file` - Retrieve downloaded file
- `GET /health` - Health check endpoint

## Security Notes

- The application runs Chrome in headless mode with sandbox disabled (required for container environments)
- CORS is enabled for API access
- No authentication is implemented - add if needed for production

## License

This project is for educational purposes. Please respect Facebook's Terms of Service and users' privacy when using this application.

## Support

For issues or questions, please create an issue in the GitHub repository.
