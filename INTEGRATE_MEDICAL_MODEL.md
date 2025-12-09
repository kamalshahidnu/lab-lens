# Quick Start: Using Medical-Specific Models

## Install Required Libraries
```bash
pip install transformers torch torchvision pillow
```

## Use Medical-Specific Model for Chest X-rays

The new `MedicalImageAnalyzerHF` class uses models specifically trained on medical images.

### Basic Usage:
```python
from src.training.medical_image_analysis_hf import MedicalImageAnalyzerHF

# Initialize analyzer with medical model
analyzer = MedicalImageAnalyzerHF(model_name='chexpert')

# Analyze chest X-ray
result = analyzer.analyze_chest_xray('path/to/chest_xray.jpg')

# Check results
print(f"Disease Present: {result['disease_present']}")
print(f"Diseases Detected: {result['diseases_detected']}")
```

### Available Models:
- `chexpert` - Stanford CheXpert classifier (recommended)
- `chexnet` - Microsoft ResNet-50 (alternative)
- `default` - Default medical model

### Advantages:
✅ Specifically trained on chest X-rays
✅ Better disease detection accuracy
✅ Won't misclassify diseased as normal
✅ Local inference (no API calls)
✅ Free and open source

### Test It:
```bash
python src/training/medical_image_analysis_hf.py /path/to/xray.jpg
```
