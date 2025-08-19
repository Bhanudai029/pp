from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Redirect to the API documentation
        self.send_response(302)
        self.send_header('Location', '/api/')
        self.end_headers()
        
    def do_POST(self):
        # Handle POST requests by redirecting to the API
        self.send_response(302)
        self.send_header('Location', '/api/')
        self.end_headers()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('', port), RedirectHandler)
    print(f"Redirect server running on port {port}")
    print("All requests will be redirected to the Node.js API in the /api directory")
    server.serve_forever()