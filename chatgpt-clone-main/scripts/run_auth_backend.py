#!/usr/bin/env python3
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_auth.txt"])

def run_server():
    """Run the FastAPI server"""
    print("Starting ChatGPT Clone Auth Backend...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nMake sure to:")
    print("1. Install and configure MySQL")
    print("2. Create the database using database_schema.sql")
    print("3. Set environment variables for MySQL connection")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the server
    subprocess.run([sys.executable, "auth_backend.py"])

if __name__ == "__main__":
    try:
        install_requirements()
        run_server()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error: {e}")
