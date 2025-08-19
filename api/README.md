# Facebook Profile Picture API

This is a simple API that allows you to download Facebook profile pictures by providing a Facebook photo URL.

## Features

- Takes a Facebook photo URL as input
- Returns a direct download link for the profile picture
- Runs headlessly to minimize resource usage
- Can be hosted on Render.com
- Uses Puppeteer for browser automation
- Returns images with the filename "Free_FB_Zone_Profile_Picture.png"

## API Endpoints

### GET /

Returns API information and available endpoints.

### GET /health

Health check endpoint for monitoring.

Response:
```json
{
  "status": "ok",
  "timestamp": "2023-08-19T10:30:00.000Z",
  "uptime": 3600.123
}
```

### POST /download

Request body:
```json
{
  "url": "https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887"
}
```

Response:
```json
{
  "success": true,
  "downloadUrl": "https://your-api-url.onrender.com/images/Free_FB_Zone_Profile_Picture.png"
}
```

### GET /images/:filename

Serves the downloaded images.

## Setup Instructions

1. Clone this repository
2. Navigate to the api directory:
   ```bash
   cd api
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the server:
   ```bash
   npm start
   ```

The server will start on port 3000 by default, or the PORT environment variable if set.

## Deployment to Render

### Method 1: Using render.yaml (Recommended)

1. Fork this repository to your GitHub account
2. Create a new Web Service on Render
3. Connect your forked repository
4. Render will automatically detect the `render.yaml` file
5. Click "Apply" and then "Create Web Service"
6. Wait for the deployment to complete

**Auto-Deploy:** This repository is configured with `autoDeploy: true` in the `render.yaml` file, which means that any new commits pushed to the main branch of your forked repository will automatically trigger a new deployment.

### Method 2: Manual Setup

1. Fork this repository to your GitHub account
2. Create a new Web Service on Render
3. Connect your forked repository
4. Set the build command to:
   ```bash
   npm install
   ```
5. Set the start command to:
   ```bash
   npm start
   ```
6. Add environment variables:
   - `NODE_ENV` = `production`
7. Deploy!

## Environment Variables

- `PORT` - The port to run the server on (default: 10000)
- `NODE_ENV` - Environment (production/development)

## Usage Example

```javascript
fetch('https://your-api-url.onrender.com/download', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    // Download the image
    window.location.href = data.downloadUrl;
  }
});
```

## Demo

A demo HTML file is included (`demo.html`) that shows how to use the API from a web frontend.

## Notes

- Facebook frequently changes its UI, so this API may need updates over time
- Some photos may not be downloadable if they are private or have privacy restrictions
- Puppeteer requires significant resources, so free tier limitations may apply on Render