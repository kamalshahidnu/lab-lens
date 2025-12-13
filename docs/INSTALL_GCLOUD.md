# Installing Google Cloud SDK (gcloud CLI) on macOS

## Quick Installation

### Option 1: Using Homebrew (Recommended - Easiest)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Google Cloud SDK
brew install --cask google-cloud-sdk
```

### Option 2: Direct Download

1. **Download the installer:**
  ```bash
  curl https://sdk.cloud.google.com | bash
  ```

2. **Restart your terminal** or run:
  ```bash
  exec -l $SHELL
  ```

3. **Initialize gcloud:**
  ```bash
  gcloud init
  ```

### Option 3: Manual Installation

1. Go to: https://cloud.google.com/sdk/docs/install
2. Download the macOS installer
3. Run the installer
4. Follow the installation wizard

## Verify Installation

After installation, verify it works:

```bash
gcloud --version
```

You should see output like:
```
Google Cloud SDK 450.0.0
bq 2.0.93
core 2024.01.12
gsutil 5.26
```

## After Installation

Once `gcloud` is installed, you can run:

```bash
./scripts/setup_gcp_auth.sh
```

## Alternative: Python-Only Authentication (No gcloud CLI)

If you prefer not to install gcloud CLI, you can authenticate directly from Python:

```bash
# Install required packages
pip install google-cloud-bigquery google-auth google-auth-oauthlib

# Authenticate (will open browser)
python -c "
from google.auth import default
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/bigquery']

# Try to use existing credentials
try:
  credentials, project = default()
  print(' Using existing credentials')
except:
  # If no credentials, run OAuth flow
  flow = InstalledAppFlow.from_client_secrets_file(
    'credentials/oauth_client.json', SCOPES)
  credentials = flow.run_local_server(port=8080)
  print(' Authentication successful')

print('You can now use BigQuery!')
"
```

However, the **gcloud CLI method is recommended** as it's simpler and more reliable.




