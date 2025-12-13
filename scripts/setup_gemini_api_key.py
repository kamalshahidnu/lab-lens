#!/usr/bin/env python3
"""
Secure setup script for Gemini API key
Creates .env file with your API key (already in .gitignore)
"""

import os
import sys
from pathlib import Path
import getpass

def setup_api_key():
  """Set up Gemini API key in .env file"""
  print("=" * 70)
  print("Gemini API Key Setup")
  print("=" * 70)
  print()
  print("This will create a .env file with your API key.")
  print("The .env file is already in .gitignore for security.")
  print()
  print("Get your API key from: https://aistudio.google.com/app/apikey")
  print()
 
  # Check if .env exists
  env_file = Path('.env')
  if env_file.exists():
    response = input("⚠️ .env file already exists. Overwrite? (y/n): ")
    if response.lower() != 'y':
      print("Aborted.")
      return
    print()
 
  # Get API key (hidden input)
  api_key = getpass.getpass("Enter your Google Gemini API key: ")
 
  if not api_key or api_key.strip() == '':
    print(" API key cannot be empty!")
    sys.exit(1)
 
  # Create .env file
  env_content = f"""# Google Gemini API Configuration
# This file is in .gitignore and will not be committed to git
# Get your API key from: https://aistudio.google.com/app/apikey

GOOGLE_API_KEY={api_key.strip()}
"""
 
  env_file.write_text(env_content)
 
  print()
  print("=" * 70)
  print(" API key saved to .env file")
  print("=" * 70)
  print()
  print("The .env file is in .gitignore, so it won't be committed to git.")
  print()
  print("You can now use Gemini without passing --api-key!")
  print()
  print("Test it:")
  print(" python src/training/gemini_inference.py --input 'Test text'")
  print()

if __name__ == "__main__":
  try:
    setup_api_key()
  except KeyboardInterrupt:
    print("\n\nAborted.")
    sys.exit(1)
  except Exception as e:
    print(f"\n Error: {e}")
    sys.exit(1)







