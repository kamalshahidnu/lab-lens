# RAG Test Solution - Memory Issues

## Problem

The RAG test is crashing during embedding generation because:
- Your dataset has **967 records** creating **62,354 chunks**
- Generating embeddings for all chunks uses a lot of memory
- The process crashes (exit code 139 = segmentation fault)

## Solution: Test with Smaller Dataset First

Create a small test file with just a few records:

```bash
# Create a small test dataset (first 5 records)
python -c "
import pandas as pd
df = pd.read_csv('data-pipeline/data/processed/processed_discharge_summaries.csv')
df.head(5).to_csv('data-pipeline/data/processed/test_small.csv', index=False)
print('✅ Created test dataset with 5 records')
"
```

Then test with this smaller file:

```bash
python scripts/quick_test_rag.py \
  --hadm-id 130656 \
  --question "What are my diagnoses?" \
  --data-path data-pipeline/data/processed/test_small.csv
```

## Why This Works

- **Smaller dataset** = fewer chunks = less memory
- **Faster** = completes in seconds instead of crashing
- **Verify functionality** = confirms RAG works before scaling up

## Alternative: Check if Embeddings Already Exist

If embeddings were generated before (even partially), they're cached. Check:

```bash
ls -lh models/rag_embeddings/
```

If you see `.pkl` files, the system will use them (much faster).

## Full Workflow

1. **Create small test dataset** (5-10 records)
2. **Test RAG works** with small dataset
3. **Once verified**, use full dataset (if you have enough memory)
4. **Embeddings are cached** - subsequent runs are fast

## Quick Test Command

```bash
# Step 1: Create small test file
python -c "import pandas as pd; df = pd.read_csv('data-pipeline/data/processed/processed_discharge_summaries.csv'); df.head(5).to_csv('data-pipeline/data/processed/test_small.csv', index=False); print('Created test file')"

# Step 2: Test with small file
python scripts/quick_test_rag.py \
  --hadm-id 130656 \
  --question "What are my diagnoses?" \
  --data-path data-pipeline/data/processed/test_small.csv
```

This should work without crashes!

