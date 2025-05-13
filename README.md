# Heroku App Deletion Safety Check

This script helps safely delete Heroku applications after verifying they've been successfully migrated to Azure. It includes multiple safety checks and user confirmations to prevent accidental deletions.

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

The script will guide you through the following steps:

1. Heroku Authentication Check
   - Verifies you're logged in to Heroku CLI
   - Shows your authenticated username

2. Custom Domain Check
   - Confirms if the app has a custom domain
   - Exits if a custom domain is detected

3. Migration Confirmation
   - Verifies if the app has been migrated to Azure
   - Requests the original .botics.co URL

4. Ping Check
   - Verifies the app is reachable at the provided URL
   - Displays response status and headers

5. Final Deletion
   - Requests final confirmation before deletion
   - Deletes the Heroku app if confirmed

## Safety Features

- Multiple confirmation steps
- Custom domain detection
- Migration verification
- URL availability check
- Final confirmation before deletion
- Detailed error messages and status updates

## Error Handling

The script includes comprehensive error handling for:
- Heroku CLI authentication issues
- Network connectivity issues
- Invalid app names
- Failed deletion attempts

## Note

Always ensure you have proper backups and have verified the migration before running this script. The deletion process cannot be undone. 