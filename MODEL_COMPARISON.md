# Medical Image Analysis Models Comparison

## Problem
Gemini 2.5 Pro is misclassifying diseased chest X-rays as normal.

## Available Models

### 1. **BiomedCLIP** (Recommended) ⭐

**Model**: Microsoft BiomedCLIP (OpenBioML/LAION)

**Training**: 
- 15 million biomedical image-text pairs
- Trained on scientific articles from PubMed Central

**Advantages**:
- ✅ Specifically trained on medical images
- ✅ Multimodal (image + text understanding)
- ✅ Zero-shot classification
- ✅ Better disease detection accuracy
- ✅ Local inference (no API calls)
- ✅ Free and open source
- ✅ Returns similarity scores for findings

**Disadvantages**:
- Requires GPU for fast inference (CPU works but slower)
- Model is large (~1-2GB)

**Usage**:
```python
from src.training.medical_image_analysis_biomedclip import MedicalImageAnalyzerBiomedCLIP
analyzer = MedicalImageAnalyzerBiomedCLIP()
result = analyzer.analyze_chest_xray('xray.jpg')
```

**Install**: `pip install transformers torch sentence-transformers`

---

### 2. **Gemini 2.5 Pro** (Current)

**Model**: Google Gemini 2.5 Pro

**Training**: 
- General multimodal model
- Not specifically trained on medical images

**Advantages**:
- ✅ Easy API access
- ✅ No local setup needed
- ✅ Multimodal capabilities

**Disadvantages**:
- ❌ Misclassifying diseased as normal
- ❌ Not optimized for medical images
- ❌ Requires API key
- ❌ API rate limits
- ❌ Safety filter issues

**Usage**:
```python
from src.training.medical_image_analysis import MedicalImageAnalyzer
analyzer = MedicalImageAnalyzer()  # Uses gemini-2.5-pro
result = analyzer.analyze_chest_xray('xray.jpg')
```

---

### 3. **CheXpert Classifier**

**Model**: Stanford CheXpert Classifier

**Training**:
- Trained on CheXpert dataset
- 14 chest X-ray findings

**Advantages**:
- ✅ Specifically for chest X-rays
- ✅ Good accuracy
- ✅ Local inference
- ✅ Free and open source

**Disadvantages**:
- Limited to 14 findings
- Only chest X-rays (not other modalities)

**Usage**:
```python
from src.training.medical_image_analysis_hf import MedicalImageAnalyzerHF
analyzer = MedicalImageAnalyzerHF(model_name='chexpert')
result = analyzer.analyze_chest_xray('xray.jpg')
```

**Install**: `pip install transformers torch torchvision`

---

## Recommendation

### **Use BiomedCLIP** for the following reasons:

1. **Better Accuracy**: Trained specifically on medical images
2. **Multimodal**: Understands both images and text
3. **Flexible**: Can check for custom findings
4. **Similarity Scores**: Get confidence levels
5. **Less Likely to Miss Diseases**: Better than Gemini 2.5 Pro

### Quick Start with BiomedCLIP:

```bash
# Install dependencies
pip install transformers torch sentence-transformers

# Test it
python src/training/medical_image_analysis_biomedclip.py /path/to/xray.jpg
```

### Comparison Table

| Feature | BiomedCLIP | Gemini 2.5 Pro | CheXpert |
|---------|-----------|----------------|----------|
| Medical Training | ✅ 15M pairs | ❌ General | ✅ CheXpert |
| Disease Detection | ✅ Excellent | ⚠️ Misses diseases | ✅ Good |
| Zero-shot | ✅ Yes | ✅ Yes | ❌ No |
| Multimodal | ✅ Yes | ✅ Yes | ❌ Image only |
| Local | ✅ Yes | ❌ API | ✅ Yes |
| Free | ✅ Yes | ✅ Yes | ✅ Yes |
| Similarity Scores | ✅ Yes | ❌ No | ✅ Yes |

---

## Migration Guide

To switch from Gemini to BiomedCLIP:

1. **Install dependencies**:
   ```bash
   pip install transformers torch sentence-transformers
   ```

2. **Update your code**:
   ```python
   # Old
   from src.training.medical_image_analysis import MedicalImageAnalyzer
   analyzer = MedicalImageAnalyzer()
   
   # New
   from src.training.medical_image_analysis_biomedclip import MedicalImageAnalyzerBiomedCLIP
   analyzer = MedicalImageAnalyzerBiomedCLIP()
   ```

3. **Same API** - the methods are similar:
   ```python
   result = analyzer.analyze_chest_xray('xray.jpg')
   print(result['disease_present'])
   print(result['diseases_detected'])
   ```

---

## Next Steps

1. ✅ BiomedCLIP integration created
2. Install dependencies
3. Test on your diseased images
4. Compare results
5. Switch to BiomedCLIP if it performs better



