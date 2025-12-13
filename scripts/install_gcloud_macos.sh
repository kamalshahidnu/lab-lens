#!/bin/bash
# Helper script to install Google Cloud SDK on macOS

set -e

echo "📦 Installing Google Cloud SDK (gcloud CLI)"
echo "============================================"
echo ""

# Check if already installed
if command -v gcloud &> /dev/null; then
  echo " gcloud is already installed!"
  gcloud --version
  exit 0
fi

# Check for Homebrew
if command -v brew &> /dev/null; then
  echo " Homebrew found - using Homebrew installation (recommended)"
  echo ""
  echo "Installing Google Cloud SDK via Homebrew..."
  brew install --cask google-cloud-sdk
 
  echo ""
  echo " Installation complete!"
  echo ""
  echo "Next steps:"
  echo "1. Restart your terminal or run: exec -l \$SHELL"
  echo "2. Run: ./scripts/setup_gcp_auth.sh"
  exit 0
fi

# If no Homebrew, provide manual instructions
echo "⚠️ Homebrew not found"
echo ""
echo "You have two options:"
echo ""
echo "Option 1: Install Homebrew first (recommended)"
echo " /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
echo " Then run this script again"
echo ""
echo "Option 2: Install gcloud directly"
echo " Run: curl https://sdk.cloud.google.com | bash"
echo " Then restart your terminal"
echo ""
echo "Option 3: Download from website"
echo " Visit: https://cloud.google.com/sdk/docs/install"
echo " Download and run the macOS installer"
echo ""

read -p "Would you like to install Homebrew now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
 
  echo ""
  echo "Installing Google Cloud SDK..."
  brew install --cask google-cloud-sdk
 
  echo ""
  echo " Installation complete!"
  echo "Please restart your terminal or run: exec -l \$SHELL"
  echo "Then run: ./scripts/setup_gcp_auth.sh"
else
  echo ""
  echo "To install gcloud manually, run:"
  echo " curl https://sdk.cloud.google.com | bash"
  echo ""
  echo "Or visit: https://cloud.google.com/sdk/docs/install"
fi




