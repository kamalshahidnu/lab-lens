#!/bin/bash
# Secure setup script for Gemini API key

echo "=" | head -c 70; echo ""
echo "Gemini API Key Setup"
echo "=" | head -c 70; echo ""
echo ""

# Check if .env already exists
if [ -f .env ]; then
  echo "⚠️ .env file already exists"
  read -p "Overwrite? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
fi

# Get API key
echo "Enter your Google Gemini API key:"
echo "(Get it from: https://aistudio.google.com/app/apikey)"
read -s API_KEY

if [ -z "$API_KEY" ]; then
  echo " API key cannot be empty!"
  exit 1
fi

# Create .env file
cat > .env << EOF
# Google Gemini API Configuration
# This file is in .gitignore and will not be committed to git

GOOGLE_API_KEY=$API_KEY
EOF

echo ""
echo " API key saved to .env file"
echo " .env is in .gitignore (secure)"
echo ""
echo "You can now use Gemini without passing --api-key!"
echo ""
echo "Test it:"
echo " python src/training/gemini_inference.py --input 'Test text'"
echo ""







