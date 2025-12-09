# Model Testing Guide

## Overview

This guide explains how to test all three model functionalities:
1. **Discharge Summary Generation/Simplification**
2. **Risk Prediction from Discharge Summaries**
3. **Disease Detection from Biomedical Images**

## Test Scripts

### Main Test Script

**File:** `scripts/test_all_models.py`

This script tests all three functionalities in one go.

### Usage

#### Test 1 & 2 (Discharge Summary + Risk Prediction)
```bash
# Test discharge summary generation and risk prediction
python scripts/test_all_models.py
```

#### Test All 3 (Including Image Disease Detection)
```bash
# Test with image
python scripts/test_all_models.py --image-path /path/to/chest_xray.jpg

# Test with custom patient info
python scripts/test_all_models.py \
    --image-path /path/to/chest_xray.jpg \
    --age 65 \
    --gender M \
    --symptoms "Chest pain, shortness of breath"
```

### Command Line Options

- `--image-path`: Path to medical image (chest X-ray, CT scan, etc.)
- `--age`: Patient age for risk prediction and image analysis
- `--gender`: Patient gender (M/F)
- `--symptoms`: Patient symptoms
- `--output`: Output file for test results (default: `test_results.json`)

## Environment Setup

### Required Environment Variables

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### Required Dependencies

Make sure you have installed:
```bash
pip install google-generativeai pillow python-dotenv
```

### NumPy Compatibility Issue

**If you encounter NumPy compatibility errors:**

The error occurs when NumPy 2.0 is installed but dependencies (pandas, scikit-learn) were compiled with NumPy 1.x.

**Solution 1: Downgrade NumPy (Recommended)**
```bash
pip install "numpy<2"
```

**Solution 2: Reinstall dependencies**
```bash
pip install --upgrade --force-reinstall pandas scikit-learn
```

**Solution 3: Use virtual environment**
```bash
# Create new environment
python -m venv venv_test
source venv_test/bin/activate  # On macOS/Linux
# or
venv_test\Scripts\activate  # On Windows

# Install compatible versions
pip install "numpy<2" pandas scikit-learn google-generativeai pillow python-dotenv
```

## Testing Individual Functionalities

### Test 1: Discharge Summary Generation

**What it tests:**
- Simplified summary generation from discharge summaries
- Patient-friendly language translation
- Key information extraction

**Expected output:**
- Simplified summary (150-200 words)
- Clear, non-technical language
- Key diagnoses, medications, and follow-up instructions

### Test 2: Risk Prediction

**What it tests:**
- Risk level prediction (Low/Medium/High)
- Risk score calculation (0-100)
- Risk factor identification
- Recommendations generation

**Expected output:**
- Risk level: LOW/MEDIUM/HIGH
- Risk score: 0-100
- Risk factors: List of identified factors
- Recommendations: Suggested actions

**Sample patient info:**
```python
patient_info = {
    'age': 65,
    'gender': 'M',
    'cleaned_text': 'discharge summary text...',
    'abnormal_lab_count': 5,
    'diagnosis_count': 4,
    'length_of_stay': 3
}
```

### Test 3: Image Disease Detection

**What it tests:**
- Disease detection from chest X-rays
- Abnormality identification
- Severity assessment
- Clinical impression generation

**Expected output:**
- Diseases detected: List of identified conditions
- Severity: Normal/Mild/Moderate/Severe
- Findings: Detailed findings from image
- Impression: Clinical interpretation

**Supported image types:**
- Chest X-rays (`.jpg`, `.jpeg`, `.png`)
- CT scans
- MRIs
- Other medical images

## Test Results

Test results are saved to `test_results.json` by default.

### Result Structure

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "discharge_summary_test": {
    "status": "success",
    "summary": "...",
    "summary_length": 185
  },
  "risk_prediction_test": {
    "status": "success",
    "risk_level": "high",
    "risk_score": 75,
    "risk_factors": {...},
    "recommendations": [...]
  },
  "image_disease_detection_test": {
    "status": "success",
    "diseases_detected": [...],
    "severity": "moderate",
    "findings": [...],
    "has_disease": true
  },
  "overall_status": "success"
}
```

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution:** Set the API key in environment:
```bash
export GOOGLE_API_KEY="your-key"
# Or add to .env file
echo "GOOGLE_API_KEY=your-key" >> .env
```

### Issue: "Image file not found"

**Solution:** Provide correct path:
```bash
# Use absolute path
python scripts/test_all_models.py --image-path /absolute/path/to/image.jpg

# Or relative path from project root
python scripts/test_all_models.py --image-path data-pipeline/data/raw/images/xray.jpg
```

### Issue: NumPy compatibility errors

**Solution:** See "NumPy Compatibility Issue" section above.

### Issue: Import errors

**Solution:** Install missing dependencies:
```bash
pip install -r requirements.txt
```

## Example Test Session

```bash
# 1. Set API key
export GOOGLE_API_KEY="your-api-key"

# 2. Test discharge summary and risk prediction
python scripts/test_all_models.py

# 3. Test with image (if you have a chest X-ray)
python scripts/test_all_models.py \
    --image-path /path/to/chest_xray.jpg \
    --age 65 \
    --gender M \
    --symptoms "Chest pain"

# 4. Check results
cat test_results.json
```

## Expected Behavior

### Successful Test Run

1. **Discharge Summary Test:**
   - ✓ Model initializes
   - ✓ Summary generated
   - ✓ Summary is readable and simplified

2. **Risk Prediction Test:**
   - ✓ Model initializes
   - ✓ Risk level predicted
   - ✓ Risk factors identified
   - ✓ Recommendations provided

3. **Image Disease Detection Test:**
   - ✓ Model initializes
   - ✓ Image analyzed
   - ✓ Diseases detected (if present)
   - ✓ Severity assessed
   - ✓ Findings extracted

## Notes

- Image analysis requires Gemini 1.5 Pro (multimodal support)
- All tests use the same API key
- Test results are saved automatically
- Tests can be run individually or together
- Image test is optional (skip if no image provided)

## Next Steps

After successful testing:
1. Integrate into production pipeline
2. Deploy to production environment
3. Set up monitoring and logging
4. Configure API rate limits
5. Set up error handling and retries



