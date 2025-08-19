#!/usr/bin/env python3
"""
This is a simple Python script to satisfy build requirements on platforms that expect Python applications.
The actual Facebook Profile Picture API is a Node.js application located in the /api directory.
"""

import os
import sys
import subprocess

def main():
    print("Facebook Profile Picture API (Node.js version)")
    print("================================================")
    print("This repository contains a Node.js API for downloading Facebook profile pictures.")
    print("To run the API, please navigate to the 'api' directory and run 'npm start'")
    print("")
    print("API Endpoints:")
    print("  POST /download - Download a Facebook profile picture")
    print("  GET /health - Health check endpoint")
    print("")
    print("For more information, see the README.md file in the api directory.")
    
    # If the script is run with a specific command, try to execute it
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "start-api":
            # Change to the api directory and start the Node.js server
            api_dir = os.path.join(os.path.dirname(__file__), "api")
            if os.path.exists(api_dir):
                try:
                    subprocess.run(["node", "server.js"], cwd=api_dir)
                except FileNotFoundError:
                    print("Error: Node.js not found. Please install Node.js to run the API.")
            else:
                print("Error: API directory not found.")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: start-api")

if __name__ == "__main__":
    main()