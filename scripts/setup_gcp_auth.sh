#!/bin/bash
# Setup script for GCP authentication to access MIMIC-III via BigQuery

set -e

echo "🔐 GCP Authentication Setup for MIMIC-III BigQuery Access"
echo "========================================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
  echo " gcloud CLI not found. Please install it first:"
  echo "  https://cloud.google.com/sdk/docs/install"
  exit 1
fi

echo " gcloud CLI found"
echo ""

# Show all authenticated accounts
echo "📋 Checking authenticated Google accounts..."
AUTHENTICATED_ACCOUNTS=$(gcloud auth list --format="value(account)" 2>/dev/null || echo "")

if [ -z "$AUTHENTICATED_ACCOUNTS" ]; then
  echo "⚠️ No authenticated accounts found"
  echo ""
  echo "🔑 You'll need to authenticate with the Google account that:"
  echo "  1. Is linked to PhysioNet (https://physionet.org/settings/cloud/)"
  echo "  2. Has MIMIC-III access approved"
  echo ""
  read -p "Press Enter to continue with authentication..."
  gcloud auth login
else
  echo " Found authenticated account(s):"
  echo "$AUTHENTICATED_ACCOUNTS" | while read account; do
    echo "  - $account"
  done
  echo ""
  echo "⚠️ IMPORTANT: Make sure you authenticate with the Google account"
  echo "  that is linked to PhysioNet and has MIMIC-III access!"
  echo ""
  echo "  If you need to use a different account, you can:"
  echo "  1. Run: gcloud auth login --account=YOUR_EMAIL@example.com"
  echo "  2. Or run: gcloud auth login (to add another account)"
  echo ""
  read -p "Continue with current account? (y/n) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Switching accounts..."
    gcloud auth login
  fi
fi

echo ""

# Check current active account
ACTIVE_ACCOUNT=$(gcloud config get-value account 2>/dev/null || echo "")
if [ -n "$ACTIVE_ACCOUNT" ]; then
  echo " Active account: $ACTIVE_ACCOUNT"
  echo ""
  echo "💡 To verify this account has PhysioNet access:"
  echo "  1. Go to: https://physionet.org/settings/cloud/"
  echo "  2. Check that $ACTIVE_ACCOUNT is linked"
  echo "  3. Verify MIMIC-III access is approved"
  echo ""
fi

# Set up Application Default Credentials
echo "📋 Setting up Application Default Credentials (ADC)..."
echo "  This allows Python scripts to authenticate automatically"
echo ""

if gcloud auth application-default print-access-token &> /dev/null; then
  CURRENT_ADC_ACCOUNT=$(gcloud auth application-default print-access-token --format="value(account)" 2>/dev/null || echo "unknown")
  echo " Application Default Credentials already configured"
  if [ "$CURRENT_ADC_ACCOUNT" != "unknown" ]; then
    echo "  Using account: $CURRENT_ADC_ACCOUNT"
  fi
  echo ""
  read -p "Re-authenticate with a different account? (y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Re-authenticating..."
    gcloud auth application-default login
  fi
else
  echo "⚠️ Application Default Credentials not configured"
  echo "  Running: gcloud auth application-default login"
  echo ""
  echo "  ⚠️ IMPORTANT: Use the same Google account that has PhysioNet access!"
  echo "  This will open a browser for authentication..."
  echo ""
  read -p "Press Enter to continue..."
  gcloud auth application-default login
fi

echo ""

# Verify access to physionet-data project
echo "🧪 Testing access to physionet-data project..."
echo ""

PROJECT_ID="physionet-data"

# Try to query a small table
QUERY="SELECT COUNT(*) as count FROM \`physionet-data.mimiciii_clinical.admissions\` LIMIT 1"

if gcloud alpha bq query --project_id="$PROJECT_ID" --use_legacy_sql=false "$QUERY" &> /dev/null; then
  echo " Successfully connected to physionet-data project!"
  echo "  You can now access MIMIC-III datasets via BigQuery"
else
  echo "⚠️ Could not verify access via gcloud CLI"
  echo "  This is okay - Python scripts will use Application Default Credentials"
  echo "  Make sure your Google account has access to MIMIC-III at:"
  echo "  https://physionet.org/settings/cloud/"
fi

echo ""
echo " Setup complete!"
echo ""
echo "Next steps:"
echo "1. Test connection: python scripts/acquire_mimic3_bigquery.py --test"
echo "2. Fetch data: python scripts/acquire_mimic3_bigquery.py --limit 1000"
echo ""

