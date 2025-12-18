#!/usr/bin/env python3
"""
Test Gemini API Setup
Diagnoses and tests the Gemini API configuration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
    sys.exit(1)


def check_api_key():
    """Check if API key is set correctly"""
    print("=" * 70)
    print("GEMINI API SETUP DIAGNOSTIC")
    print("=" * 70)
    print()

    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f" .env file found: {env_file.absolute()}")
        try:
            with open(env_file, "r") as f:
                content = f.read()
                if "GOOGLE_API_KEY" in content:
                    print(" GOOGLE_API_KEY found in .env file")
                else:
                    print(" GOOGLE_API_KEY not found in .env file")
        except Exception as e:
            print(f" Error reading .env file: {e}")
    else:
        print(" .env file not found")

    print()

    # Check environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        key_length = len(api_key)
        if key_length > 20:  # Valid API keys are typically 30-40 characters
            print(f" GOOGLE_API_KEY is set in environment")
            print(f"  Key length: {key_length} characters")
            print(f"  Key starts with: {api_key[:10]}...")
            print(f"  Key ends with: ...{api_key[-4:]}")
            return api_key
        else:
            print(f" GOOGLE_API_KEY appears to be invalid (too short: {key_length} characters)")
            print(f"  Current value: '{api_key}'")
            print()
            print("  Valid Gemini API keys are typically 30-40 characters long")
            print("  and start with 'AIza'")
            return None
    else:
        print(" GOOGLE_API_KEY not set in environment")
        return None


def test_api_connection(api_key):
    """Test the API connection"""
    print()
    print("=" * 70)
    print("TESTING API CONNECTION")
    print("=" * 70)
    print()

    try:
        import google.generativeai as genai

        print(" google-generativeai package installed")
    except ImportError:
        print(" google-generativeai package not installed")
        print("  Install with: pip install google-generativeai")
        return False

    try:
        # Suppress warnings
        os.environ["GRPC_VERBOSITY"] = "ERROR"
        os.environ["GRPC_PYTHON_LOG_LEVEL"] = "ERROR"

        # Configure API
        genai.configure(api_key=api_key)
        print(" API configured successfully")

        # Test with a simple model list or generation
        print("⏳ Testing API connection...")

        # Try to list models (lightweight test)
        try:
            models = list(genai.list_models())
            print(f" API connection successful! Found {len(models)} available models")
            print()
            print("Available models:")
            for model in models[:5]:  # Show first 5
                if "generateContent" in model.supported_generation_methods:
                    print(f" - {model.name}")
            return True
        except Exception as e:
            # If list_models fails, try a simple generation
            print(f"⚠️ Could not list models: {e}")
            print("⏳ Trying simple generation test...")

            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content("Say 'Hello' in one word.")
            print(f" API connection successful! Response: {response.text.strip()}")
            return True

    except Exception as e:
        print(f" API connection failed: {e}")
        print()
        print("Common issues:")
        print(" 1. Invalid API key - check that your key is correct")
        print(" 2. API quota exceeded - check your usage limits")
        print(" 3. Network connectivity issues")
        print(" 4. API key not enabled for the model you're trying to use")
        return False


def print_setup_instructions():
    """Print setup instructions"""
    print()
    print("=" * 70)
    print("SETUP INSTRUCTIONS")
    print("=" * 70)
    print()
    print("1. Get your API key from:")
    print("  https://aistudio.google.com/app/apikey")
    print()
    print("2. Run the setup script:")
    print("  python scripts/setup_gemini_api_key.py")
    print()
    print("  OR manually create/edit .env file:")
    print("  GOOGLE_API_KEY=your-api-key-here")
    print()
    print("3. Verify setup:")
    print("  python scripts/test_gemini_setup.py")
    print()


def main():
    api_key = check_api_key()

    if api_key and len(api_key) > 20:
        if test_api_connection(api_key):
            print()
            print("=" * 70)
            print(" GEMINI API SETUP COMPLETE!")
            print("=" * 70)
            print()
            print("You can now use the RAG system:")
            print(" python scripts/test_rag_with_record.py --test 130656")
            print()
        else:
            print_setup_instructions()
    else:
        print_setup_instructions()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
