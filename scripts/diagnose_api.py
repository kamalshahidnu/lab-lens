#!/usr/bin/env python3
"""
Comprehensive API Diagnostic Script
Checks API key, available models, and tests image analysis capability
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_api_key():
  """Check if API key is set"""
  print('='*70)
  print('1. API KEY CHECK')
  print('='*70)
 
  api_key = os.getenv('GOOGLE_API_KEY')
 
  # Check various sources
  print(f'Checking GOOGLE_API_KEY from environment...')
  if api_key:
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
    print(f' API Key found: {masked_key}')
    print(f'  Length: {len(api_key)} characters')
    return api_key
  else:
    print(' GOOGLE_API_KEY not found in environment')
    print()
    print('Possible sources to check:')
    print(' 1. Environment variable: echo $GOOGLE_API_KEY')
    print(' 2. .env file in project root')
    print(' 3. Shell config files (.bashrc, .zshrc, etc.)')
    print()
    print('To set it:')
    print(' export GOOGLE_API_KEY="your-api-key"')
    print(' # Or add to .env file: GOOGLE_API_KEY=your-api-key')
    return None


def list_available_models():
  """List all available Gemini models"""
  print()
  print('='*70)
  print('2. AVAILABLE MODELS')
  print('='*70)
 
  try:
    models = genai.list_models()
   
    image_capable = []
    text_only = []
    pro_models = []
    flash_models = []
   
    for model in models:
      name = model.name
      methods = model.supported_generation_methods
     
      # Check for generateContent (image support)
      if 'generateContent' in methods:
        name_lower = name.lower()
        if 'pro' in name_lower:
          pro_models.append(name)
        if 'flash' in name_lower:
          flash_models.append(name)
       
        if 'vision' in name_lower or 'flash' in name_lower or 'pro' in name_lower or '2.5' in name_lower:
          image_capable.append(name)
        else:
          text_only.append(name)
   
    print(f'Found {len(image_capable)} image-capable models')
    print()
   
    # Check specifically for 2.5-pro
    print('🔍 Looking for gemini-2.5-pro...')
    gemini_25_pro = None
    for model in image_capable:
      if '2.5' in model.lower() and 'pro' in model.lower():
        gemini_25_pro = model
        print(f' Found: {model}')
        break
   
    if not gemini_25_pro:
      print(' gemini-2.5-pro not found')
      print()
      print('Available Pro models:')
      for model in pro_models[:5]:
        print(f'  • {model}')
      if len(pro_models) > 5:
        print(f'  ... and {len(pro_models) - 5} more')
      print()
      print('Available Flash models (known to work with images):')
      for model in flash_models[:5]:
        print(f'  • {model}')
      if len(flash_models) > 5:
        print(f'  ... and {len(flash_models) - 5} more')
   
    return gemini_25_pro, image_capable
   
  except Exception as e:
    print(f' Error listing models: {e}')
    import traceback
    traceback.print_exc()
    return None, []


def test_model_initialization():
  """Test initializing different models"""
  print()
  print('='*70)
  print('3. MODEL INITIALIZATION TEST')
  print('='*70)
 
  models_to_test = [
    'gemini-2.5-pro',
    'models/gemini-2.5-pro',
    'gemini-2.5-pro-latest',
    'gemini-1.5-pro', # Fallback
    'gemini-1.5-flash', # Known working
    'gemini-1.5-flash-latest'
  ]
 
  working_models = []
 
  for model_name in models_to_test:
    try:
      model = genai.GenerativeModel(model_name)
      print(f' {model_name:30s} - Initializes OK')
      working_models.append(model_name)
    except Exception as e:
      error_str = str(e)
      if '404' in error_str:
        print(f' {model_name:30s} - 404 Not Found')
      else:
        print(f'⚠️ {model_name:30s} - {str(e)[:60]}')
 
  return working_models


def test_image_analysis():
  """Test actual image analysis capability"""
  print()
  print('='*70)
  print('4. IMAGE ANALYSIS CAPABILITY TEST')
  print('='*70)
 
  # Try to find a test image
  test_dirs = [
    Path('data/raw/images'),
    Path('test_images'),
    Path('samples'),
    Path.home() / 'Downloads'
  ]
 
  test_image = None
  for test_dir in test_dirs:
    if test_dir.exists():
      for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        for img_file in test_dir.glob(f'*{ext}'):
          test_image = img_file
          break
        if test_image:
          break
      if test_image:
        break
 
  if not test_image:
    print('⚠️ No test image found')
    print('  Skipping image analysis test')
    print('  (Place an image in data/raw/images/ to test)')
    return False
 
  print(f'Found test image: {test_image}')
  print()
 
  # Test with gemini-2.5-pro
  print('Testing with gemini-2.5-pro...')
  try:
    from src.training.medical_image_analysis import MedicalImageAnalyzer
    from PIL import Image
   
    analyzer = MedicalImageAnalyzer()
    print(f' Analyzer initialized with: {analyzer.model_name}')
   
    # Try a simple image load first
    img = Image.open(test_image)
    print(f' Image loaded: {img.size[0]}x{img.size[1]} pixels')
   
    # Try actual analysis
    print('Attempting image analysis...')
    result = analyzer.analyze_medical_image(test_image, image_type='chest_xray')
   
    print(' Image analysis successful!')
    print(f'  Model used: {result.get("model_used", "unknown")}')
    print(f'  Findings: {len(result.get("findings", []))} findings')
    return True
   
  except Exception as e:
    error_str = str(e)
    print(f' Image analysis failed: {e}')
    print()
   
    if '404' in error_str or 'not found' in error_str:
      print('🔍 Issue: Model not found or doesn\'t support images')
      print('  This means gemini-2.5-pro may not be available for image analysis')
      print('  Consider using gemini-1.5-flash instead')
    elif 'api' in error_str.lower() or 'key' in error_str.lower():
      print('🔍 Issue: API key problem')
      print('  Check your GOOGLE_API_KEY')
    elif 'image' in error_str.lower() or 'format' in error_str.lower():
      print('🔍 Issue: Image format problem')
    else:
      print('🔍 Full error details:')
      import traceback
      traceback.print_exc()
   
    return False


def main():
  """Run all diagnostic checks"""
  print()
  print('╔' + '═'*68 + '╗')
  print('║' + ' '*20 + 'API DIAGNOSTIC TOOL' + ' '*29 + '║')
  print('╚' + '═'*68 + '╝')
  print()
 
  # Step 1: Check API key
  api_key = check_api_key()
  if not api_key:
    print()
    print(' Cannot continue without API key')
    print('  Please set GOOGLE_API_KEY and try again')
    sys.exit(1)
 
  # Configure genai
  genai.configure(api_key=api_key)
 
  # Step 2: List available models
  gemini_25_pro, image_models = list_available_models()
 
  # Step 3: Test model initialization
  working_models = test_model_initialization()
 
  # Step 4: Test image analysis
  image_test_passed = test_image_analysis()
 
  # Summary
  print()
  print('='*70)
  print('DIAGNOSTIC SUMMARY')
  print('='*70)
  print()
 
  print(f' API Key: {'Set' if api_key else 'Not Set'}')
  print(f' gemini-2.5-pro available: {'Yes' if gemini_25_pro else 'No'}')
  print(f' Model initialization: {len(working_models)} models work')
  print(f' Image analysis: {'Works' if image_test_passed else 'Failed'}')
  print()
 
  if not gemini_25_pro:
    print('⚠️ RECOMMENDATION:')
    print('  gemini-2.5-pro is not available in your API.')
    print('  Consider updating the code to use a working model like:')
    for model in working_models:
      if 'flash' in model.lower():
        print(f'  • {model} (recommended for images)')
        break
    print()
 
  print('='*70)


if __name__ == '__main__':
  main()



