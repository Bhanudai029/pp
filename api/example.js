// Example usage of the Facebook Profile Picture API
// This script demonstrates how to use the API to download a Facebook profile picture

const axios = require('axios');

// Replace with your deployed API URL or use localhost for testing
const API_URL = 'http://localhost:3000'; // Change this to your Render.com URL when deployed

async function downloadProfilePicture(facebookUrl) {
  try {
    console.log('Requesting profile picture download...');
    
    // Make request to the API
    const response = await axios.post(`${API_URL}/download`, {
      url: facebookUrl
    });
    
    if (response.data.success) {
      console.log('Download successful!');
      console.log('Download URL:', response.data.downloadUrl);
      
      // You can now download the image from downloadUrl
      // or display it in your application
      return response.data.downloadUrl;
    } else {
      console.error('API Error:', response.data.error);
      return null;
    }
  } catch (error) {
    console.error('Request failed:', error.message);
    return null;
  }
}

// Example usage
async function main() {
  // Example Facebook photo URL
  const facebookUrl = 'https://www.facebook.com/photo/?fbid=105948795901555&set=a.105948809234887';
  
  const downloadUrl = await downloadProfilePicture(facebookUrl);
  
  if (downloadUrl) {
    console.log('\nYou can now:');
    console.log('- Download the image directly from the URL');
    console.log('- Display it in your web application');
    console.log('- Save it to your server');
  }
}

// Run the example
main();