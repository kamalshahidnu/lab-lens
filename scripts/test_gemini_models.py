#!/usr/bin/env python3
"""
Test script to check available Gemini models
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
  import google.generativeai as genai
 
  api_key = os.getenv('GOOGLE_API_KEY')
  if not api_key:
    print(" GOOGLE_API_KEY not found in environment")
    print("Make sure you've run: python scripts/setup_gemini_api_key.py")
    sys.exit(1)
 
  genai.configure(api_key=api_key)
 
  print("=" * 70)
  print("Available Gemini Models")
  print("=" * 70)
  print()
 
  # List available models
  models = genai.list_models()
 
  available_models = []
  for model in models:
    if 'generateContent' in model.supported_generation_methods:
      model_name = model.name.replace('models/', '')
      available_models.append(model_name)
      print(f" {model_name}")
 
  print()
  print("=" * 70)
  print(f"Found {len(available_models)} available models")
  print("=" * 70)
  print()
 
  # Test recommended models
  recommended = ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
 
  print("Testing recommended models:")
  print("-" * 70)
 
  for model_name in recommended:
    if model_name in available_models:
      try:
        model = genai.GenerativeModel(model_name)
        print(f" {model_name} - Available and working")
      except Exception as e:
        print(f" {model_name} - Error: {str(e)[:50]}")
    else:
      print(f"○ {model_name} - Not in available models list")
 
  print()
  print("Recommended: Use the first available model from the list above")
 
except ImportError:
  print(" google-generativeai not installed")
  print("Install with: pip install google-generativeai")
  sys.exit(1)
except Exception as e:
  print(f" Error: {e}")
  sys.exit(1)






