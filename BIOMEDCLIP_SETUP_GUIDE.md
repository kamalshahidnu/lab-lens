# BiomedCLIP API Setup Guide

## Complete Setup Instructions

### Step 1: Get Hugging Face API Token

1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Enter a name (e.g., "lab-lens-api")
4. Select **"Read"** access (sufficient for inference)
5. Click **"Generate token"**
6. **Copy the token** (starts with `hf_...`)

⚠️ **Important**: Copy the token immediately - you won't be able to see it again!

### Step 2: Run Setup Script

Choose one of these methods:

#### Option A: Python Setup (Recommended)
```bash
python scripts/setup_biomedclip_api.py
```

#### Option B: Shell Script
```bash
bash scripts/setup_biomedclip_api.sh
```

#### Option C: Manual Setup
```bash
# Set environment variable
export HUGGINGFACE_API_TOKEN="your-token-here"

# Add to .env file
echo "HUGGINGFACE_API_TOKEN=your-token-here" >> .env
```

### Step 3: Install Dependencies

```bash
pip install requests pillow
# Optional but recommended:
pip install huggingface_hub
```

### Step 4: Test Setup

```bash
python scripts/test_biomedclip_api.py
```

This will verify:
- ✅ API token is set correctly
- ✅ Required libraries are installed
- ✅ API connection works
- ✅ BiomedCLIP analyzer is ready

### Step 5: Use BiomedCLIP

Now you can use BiomedCLIP for medical image analysis:

```bash
# Interactive script (automatically uses BiomedCLIP if available)
python scripts/interactive_image_disease_detection.py
```

Or in Python:
```python
from src.training.medical_image_analysis_biomedclip_api import MedicalImageAnalyzerBiomedCLIP_API

analyzer = MedicalImageAnalyzerBiomedCLIP_API()
result = analyzer.analyze_chest_xray('path/to/xray.jpg')
print(f"Disease Present: {result['disease_present']}")
```

## Verification

Check if setup is complete:
```bash
# Check token is set
echo $HUGGINGFACE_API_TOKEN

# Test API connection
python scripts/test_biomedclip_api.py
```

## Troubleshooting

### Token not found
- Run: `python scripts/setup_biomedclip_api.py`
- Or manually: `export HUGGINGFACE_API_TOKEN="your-token"`

### Libraries missing
```bash
pip install requests pillow huggingface_hub
```

### API connection fails
- Check your internet connection
- Verify token is valid at: https://huggingface.co/settings/tokens
- Check rate limits (free tier has limits)

### First request takes long
- Normal! Model needs to load on Hugging Face servers
- First request: 30-60 seconds
- Subsequent requests: 5-10 seconds

## Next Steps

1. ✅ Setup complete
2. Test with your images
3. Compare results with Gemini
4. Use BiomedCLIP for better disease detection!

---

**Need help?** Run: `python scripts/test_biomedclip_api.py` to diagnose issues.



