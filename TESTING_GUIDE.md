# Disease Detection Model Testing Guide

## ✅ Model Verification Complete!

The model has been verified and is ready for testing:
- ✅ Model initialized: `gemini-2.5-pro`
- ✅ Prompt engineering: Disease-focused prompts active
- ✅ Response parsing: Enhanced extraction ready
- ✅ Safety settings: Configured for medical images

## 🧪 How to Test

### Option 1: Interactive Test (Recommended)

Run the interactive script with file picker:

```bash
python scripts/interactive_image_disease_detection.py
```

**Steps:**
1. Press Enter (or type `1`) to open file picker
2. Select your medical image (JPEG, PNG, etc.)
3. Optionally provide patient information
4. Wait for analysis (10-30 seconds)
5. View disease prediction results

### Option 2: Direct Test Script

Test with a specific image file:

```bash
python scripts/test_disease_detection.py /path/to/your/image.jpg
```

**Example:**
```bash
python scripts/test_disease_detection.py ~/Downloads/chest_xray.png
```

### Option 3: Test Different Image Types

```bash
# Chest X-ray
python scripts/test_disease_detection.py image.jpg --image-type chest_xray

# CT scan
python scripts/test_disease_detection.py ct_scan.jpg --image-type ct_scan

# MRI
python scripts/test_disease_detection.py mri.jpg --image-type mri
```

## 📊 What to Expect

The model will provide:

1. **Disease Detection**
   - Yes/No disease presence
   - List of detected diseases with confidence levels (High/Medium/Low)

2. **Disease Prediction**
   - Primary diagnosis
   - Differential diagnoses (ranked)
   - Severity: Mild/Moderate/Severe/Critical
   - Urgency: Routine/Urgent/Emergency

3. **Clinical Information**
   - Disease summary (brief explanation)
   - Clinical findings
   - Recommendations

## 🎯 Example Output

```
======================================================================
DISEASE DETECTION RESULTS
======================================================================

🚨 DISEASE DETECTED: YES

📋 DISEASES DETECTED:
   1. Pneumonia (Confidence: High)
   2. Pleural effusion (Confidence: Medium)

🎯 PRIMARY DIAGNOSIS: Bacterial pneumonia with pleural effusion

🔍 DIFFERENTIAL DIAGNOSES:
   1. Viral pneumonia
   2. Tuberculosis

⚠️  SEVERITY: MODERATE
🚨 URGENCY: URGENT

📝 DISEASE SUMMARY:
Pneumonia with pleural effusion detected in the right lower lobe...
```

## 🔧 Troubleshooting

### If you get API errors:

1. **Check API Key:**
   ```bash
   echo $GOOGLE_API_KEY
   ```

2. **Set API Key if missing:**
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   ```

3. **Run diagnostic:**
   ```bash
   python scripts/diagnose_api.py
   ```

### If you get safety filter errors:

- The safety settings have been configured to allow medical content
- Some images may still trigger filters
- Try a different image or contact API support for medical use case exemptions

### If model doesn't detect diseases:

- Ensure image is clear and properly formatted
- Check that image type matches (chest X-ray, CT scan, etc.)
- Try providing patient information for better context

## 📝 Test Checklist

- [ ] Model initializes successfully
- [ ] Image loads correctly
- [ ] Disease detection works (Yes/No)
- [ ] Diseases listed with confidence levels
- [ ] Primary diagnosis provided
- [ ] Severity and urgency assessed
- [ ] Disease summary generated
- [ ] Recommendations provided

## 🚀 Next Steps

After testing, you can:

1. Integrate into pipeline: Use in `data-pipeline/scripts/image_analysis.py`
2. Batch processing: Process multiple images at once
3. Customize prompts: Adjust for specific use cases
4. Add to model registry: Track model performance

---

**Need help?** Check the diagnostic script:
```bash
python scripts/diagnose_api.py
```



