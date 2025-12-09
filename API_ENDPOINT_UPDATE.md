# Hugging Face API Endpoint Update

## Issue Fixed

Hugging Face deprecated the old API endpoint:
- ❌ Old: `https://api-inference.huggingface.co`
- ✅ New: `https://router.huggingface.co`

## Changes Made

Updated all API endpoints in `medical_image_analysis_biomedclip_api.py`:

1. **Main API URL**: Updated to use router endpoint
2. **Image embedding endpoint**: Changed to router format
3. **Text embedding endpoint**: Changed to router format

## Updated Endpoints

All endpoints now use:
```
https://router.huggingface.co/models/{MODEL_ID}
```

Instead of:
```
https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL_ID}
```

## Testing

Try running the pre-computation script again:

```bash
python scripts/precompute_biomedclip_embeddings.py
```

If you still encounter errors, the InferenceClient should automatically use the correct endpoint. The `huggingface_hub.InferenceClient` handles the router endpoint internally.

## Note

The Hugging Face InferenceClient (when using `huggingface_hub`) automatically handles the router endpoint, so if you're using the client, it should work seamlessly. The direct requests have been updated to use the new router endpoint.



