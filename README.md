# Heroku App Deletion Safety Check

This script helps safely delete Heroku applications after verifying they've been successfully migrated to Azure. It includes multiple safety checks and user confirmations to prevent accidental deletions. The script supports processing multiple apps in a single session.

## Prerequisites

- Python 3.6 or higher
- Heroku CLI installed and authenticated
- Required Python packages (listed in requirements.txt)

## Setup

1. Clone this repository or download the script files.

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you're authenticated with Heroku CLI:
   ```bash
   heroku login
   ```

## Usage

Run the script:
```bash
python heroku_cleanup.py
```

The script will guide you through the following steps for each app:

1. Heroku Authentication Check
   - Verifies you're logged in to Heroku CLI
   - Shows your authenticated username

2. Custom Domain Check
   - Confirms if the app has a custom domain
   - Skips the app if a custom domain is detected

3. Migration Confirmation
   - Verifies if the app has been migrated to Azure
   - Requests the original .botics.co URL

4. Ping Check
   - Verifies basic network connectivity
   - Displays ping results

5. HTTP Check
   - Verifies the app is reachable at the provided URL
   - Displays response status and headers

6. Final Deletion
   - Requests final confirmation before deletion
   - Deletes the Heroku app if confirmed

7. Continue Option
   - After each app is processed, asks if you want to process another app
   - Allows you to delete multiple apps in one session
   - Exit the script when you're done

## Multi-App Processing

The script supports processing multiple apps in a single session:
- After each app is processed (whether deleted or skipped), you'll be asked if you want to process another app
- You can continue processing apps until you're done
- Each app is processed independently with its own set of checks
- You can exit the script at any time by answering 'no' to the continue prompt

## Safety Features

- Multiple confirmation steps
- Custom domain detection
- Migration verification
- Network connectivity check (ping)
- HTTP availability check
- Final confirmation before deletion
- Detailed error messages and status updates
- Independent processing of each app

## Error Handling

The script includes comprehensive error handling for:
- Heroku CLI authentication issues
- Network connectivity issues
- Invalid app names
- Failed deletion attempts
- Failed ping attempts
- HTTP request failures

## Note

Always ensure you have proper backups and have verified the migration before running this script. The deletion process cannot be undone. 