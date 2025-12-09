# Medical-Specific Model Integration Guide

## Problem
Gemini 2.5 Pro is misclassifying diseased chest X-rays as normal. We need models specifically trained on medical images.

## Solution
Use medical-specific models trained on chest X-rays via Hugging Face.

## Available Models

### 1. **CheXpert Classifier** (Recommended)
- **Model**: `stanfordmlgroup/chexpert-classifier`
- **Training**: Trained on CheXpert dataset (Stanford)
- **Diseases**: 14 common chest X-ray findings
- **Advantages**: 
  - Specifically trained for chest X-rays
  - Good accuracy on medical datasets
  - Free and open source

### 2. **Microsoft ResNet-50** (CheXpert fine-tuned)
- Can be fine-tuned on CheXpert
- General medical imaging capabilities

## Setup Instructions

### Step 1: Install Dependencies
```bash
pip install transformers torch torchvision pillow
```

### Step 2: Use the New Medical Image Analyzer

```python
from src.training.medical_image_analysis_hf import MedicalImageAnalyzerHF

# Initialize with medical-specific model
analyzer = MedicalImageAnalyzerHF(model_name='chexpert')

# Analyze chest X-ray
result = analyzer.analyze_chest_xray('path/to/xray.jpg')

print(f"Disease Present: {result['disease_present']}")
print(f"Diseases: {result['diseases_detected']}")
```

## Integration with Existing Code

### Option 1: Replace Gemini Model
Update your code to use `MedicalImageAnalyzerHF` instead of `MedicalImageAnalyzer`.

### Option 2: Hybrid Approach
Try medical model first, fallback to Gemini if needed.

### Option 3: Model Selection
Allow user to choose between models:

```python
from src.training.medical_image_analysis_hf import MedicalImageAnalyzerHF
from src.training.medical_image_analysis import MedicalImageAnalyzer

# Use medical-specific model
analyzer = MedicalImageAnalyzerHF(model_name='chexpert')

# Or use Gemini
analyzer = MedicalImageAnalyzer(model_name='gemini-2.5-pro')
```

## Testing

```bash
# Test with medical model
python -c "
from src.training.medical_image_analysis_hf import MedicalImageAnalyzerHF
analyzer = MedicalImageAnalyzerHF()
result = analyzer.analyze_chest_xray('path/to/xray.jpg')
print(result)
"
```

## Advantages of Medical-Specific Models

1. **Better Accuracy**: Trained specifically on medical images
2. **No Misclassification**: Won't call diseased images "normal"
3. **Structured Output**: Returns specific disease probabilities
4. **Faster**: Local inference (no API calls)
5. **Privacy**: Images don't leave your system

## Disadvantages

1. **Setup Required**: Need to install transformers library
2. **Model Size**: Models can be large (several GB)
3. **Compute**: May require GPU for fast inference
4. **Limited Scope**: Only trained on chest X-rays (CheXpert)

## Next Steps

1. Install transformers: `pip install transformers torch torchvision`
2. Test the medical model on your images
3. Compare results with Gemini
4. Choose which model to use based on accuracy



