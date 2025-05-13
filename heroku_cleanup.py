#!/usr/bin/env python3

import os
import sys
import requests
import subprocess
from dotenv import load_dotenv
from typing import Optional

def get_user_input(prompt: str) -> str:
    """Get user input and convert to lowercase."""
    return input(prompt).strip().lower()

def check_custom_domain() -> bool:
    """Check if the app has a custom domain."""
    response = get_user_input("Does the app have a custom domain (not using .botics.co)? (yes/no): ")
    return response == 'yes'

def verify_migration() -> Optional[str]:
    """Verify if the app has been migrated to Azure."""
    response = get_user_input("Has this app been migrated to Azure and is now running there? (yes/no): ")
    if response != 'yes':
        print("Migration not confirmed. Exiting without deletion.")
        return None
    
    return get_user_input("Please provide the original .botics.co URL of the app (e.g., example.botics.co): ")

def check_ping(hostname: str) -> bool:
    """Check if the host is reachable using ping."""
    try:
        # Extract hostname from URL if needed
        if '://' in hostname:
            from urllib.parse import urlparse
            hostname = urlparse(hostname).netloc
        
        print(f"\nPinging {hostname}...")
        # Use appropriate ping command based on platform
        if sys.platform == "win32":
            # Windows ping
            result = subprocess.run(['ping', '-n', '4', hostname], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True)
        else:
            # Unix-like systems (macOS, Linux)
            result = subprocess.run(['ping', '-c', '4', hostname], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True)
        
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ping failed: {e.stderr}")
        return False

def check_app_availability(url: str) -> bool:
    """Check if the app is reachable at the given URL."""
    try:
        # Ensure URL has proper format
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        # First check basic connectivity with ping
        if not check_ping(url):
            print("Basic connectivity check failed. The host might be down.")
            return False
        
        print(f"\nChecking HTTP response for {url}...")
        response = requests.get(url, timeout=10)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        return response.status_code < 400
    except requests.RequestException as e:
        print(f"Error checking HTTP response: {str(e)}")
        return False

def check_heroku_auth() -> bool:
    """Check if user is authenticated with Heroku CLI."""
    try:
        result = subprocess.run(['heroku', 'auth:whoami'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(f"Authenticated as: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("Error: Not authenticated with Heroku CLI.")
        print("Please run 'heroku login' first.")
        return False

def delete_heroku_app(app_name: str) -> bool:
    """Delete the Heroku app using the Heroku CLI."""
    try:
        # Delete the app using Heroku CLI
        result = subprocess.run(['heroku', 'apps:destroy', '--app', app_name, '--confirm', app_name],
                              capture_output=True,
                              text=True,
                              check=True)
        print(f"Successfully deleted Heroku app: {app_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error deleting Heroku app: {e.stderr}")
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    print("=== Heroku App Deletion Safety Check ===")
    
    # Check Heroku authentication
    if not check_heroku_auth():
        sys.exit(1)
    
    # Step 1: Check for custom domain
    if check_custom_domain():
        print("Custom domain detected. Exiting without deletion.")
        sys.exit(0)
    
    # Step 2: Verify migration
    botics_url = verify_migration()
    if not botics_url:
        sys.exit(0)
    
    # Step 3: Check app availability
    if not check_app_availability(botics_url):
        print("App is not reachable. Exiting without deletion.")
        sys.exit(0)
    
    # Step 4: Final confirmation and deletion
    app_name = botics_url.split('.')[0]  # Extract app name from URL
    confirmation = get_user_input(f"\nThe app appears to be running correctly on Azure. Proceed with deleting Heroku app '{app_name}'? (yes/no): ")
    
    if confirmation == 'yes':
        if delete_heroku_app(app_name):
            print("Heroku app deletion completed successfully.")
        else:
            print("Failed to delete Heroku app.")
    else:
        print("Deletion cancelled by user.")

if __name__ == "__main__":
    main() 