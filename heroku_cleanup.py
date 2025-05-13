#!/usr/bin/env python3

import os
import sys
import requests
import subprocess
from dotenv import load_dotenv
from typing import Optional
from colorama import init, Fore, Style

# Initialize colorama
init()

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

def analyze_ping_output(output: str) -> tuple[bool, str]:
    """Analyze ping output to determine if it's pointing to Azure or Heroku."""
    if "herokudns.com" in output:
        return False, "Heroku"
    elif "cloudapp.azure.com" in output:
        return True, "Azure"
    return None, "Unknown"

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
        
        # Analyze the ping output
        is_azure, platform = analyze_ping_output(result.stdout)
        
        # Color code the output
        if is_azure is True:
            print(f"{Fore.GREEN}✓ DNS is pointing to Azure{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{result.stdout}{Style.RESET_ALL}")
        elif is_azure is False:
            print(f"{Fore.YELLOW}⚠ DNS is still pointing to Heroku{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{result.stdout}{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}? DNS points to unknown platform{Style.RESET_ALL}")
            print(f"{Fore.BLUE}{result.stdout}{Style.RESET_ALL}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Ping failed: {e.stderr}{Style.RESET_ALL}")
        return False

def check_app_availability(url: str) -> bool:
    """Check if the app is reachable at the given URL."""
    try:
        # Ensure URL has proper format
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        # First check basic connectivity with ping
        if not check_ping(url):
            print(f"{Fore.RED}Basic connectivity check failed. The host might be down.{Style.RESET_ALL}")
            return False
        
        print(f"\nChecking HTTP response for {url}...")
        response = requests.get(url, timeout=10)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        return response.status_code < 400
    except requests.RequestException as e:
        print(f"{Fore.RED}Error checking HTTP response: {str(e)}{Style.RESET_ALL}")
        return False

def check_heroku_auth() -> bool:
    """Check if user is authenticated with Heroku CLI."""
    try:
        result = subprocess.run(['heroku', 'auth:whoami'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(f"{Fore.GREEN}Authenticated as: {result.stdout.strip()}{Style.RESET_ALL}")
        return True
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}Error: Not authenticated with Heroku CLI.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please run 'heroku login' first.{Style.RESET_ALL}")
        return False

def delete_heroku_app(app_name: str) -> bool:
    """Delete the Heroku app using the Heroku CLI."""
    try:
        # Delete the app using Heroku CLI
        result = subprocess.run(['heroku', 'apps:destroy', '--app', app_name, '--confirm', app_name],
                              capture_output=True,
                              text=True,
                              check=True)
        print(f"{Fore.GREEN}Successfully deleted Heroku app: {app_name}{Style.RESET_ALL}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error deleting Heroku app: {e.stderr}{Style.RESET_ALL}")
        return False

def process_single_app() -> bool:
    """Process a single app deletion workflow."""
    print(f"\n{Fore.CYAN}=== Processing New App ==={Style.RESET_ALL}")
    
    # Step 1: Check for custom domain
    if check_custom_domain():
        print(f"{Fore.YELLOW}Custom domain detected. Skipping this app.{Style.RESET_ALL}")
        return False
    
    # Step 2: Verify migration
    botics_url = verify_migration()
    if not botics_url:
        return False
    
    # Step 3: Check app availability
    if not check_app_availability(botics_url):
        print(f"{Fore.RED}App is not reachable. Skipping this app.{Style.RESET_ALL}")
        return False
    
    # Step 4: Final confirmation and deletion
    app_name = botics_url.split('.')[0]  # Extract app name from URL
    confirmation = get_user_input(f"\nThe app appears to be running correctly on Azure. Proceed with deleting Heroku app '{app_name}'? (yes/no): ")
    
    if confirmation == 'yes':
        if delete_heroku_app(app_name):
            print(f"{Fore.GREEN}Heroku app deletion completed successfully.{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Failed to delete Heroku app.{Style.RESET_ALL}")
            return False
    else:
        print(f"{Fore.YELLOW}Deletion cancelled by user.{Style.RESET_ALL}")
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    print(f"{Fore.CYAN}=== Heroku App Deletion Safety Check ==={Style.RESET_ALL}")
    
    # Check Heroku authentication
    if not check_heroku_auth():
        sys.exit(1)
    
    while True:
        # Process a single app
        process_single_app()
        
        # Ask if user wants to process another app
        continue_deletion = get_user_input(f"\n{Fore.CYAN}Do you want to process another app? (yes/no): {Style.RESET_ALL}")
        if continue_deletion != 'yes':
            print(f"\n{Fore.GREEN}Thank you for using the Heroku App Deletion Safety Check!{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    main() 