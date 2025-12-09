# RAG Quick Start Guide - Testing Without Embedding Generation

The RAG system is working, but generating embeddings for 62,000+ chunks can take time and memory. Here's how to test it efficiently:

## Option 1: Use a Smaller Test Dataset (Recommended)

Create a small test file with just a few records:

```bash
# Create a small test dataset (first 10 records)
python -c "
import pandas as pd
df = pd.read_csv('data-pipeline/data/processed/processed_discharge_summaries.csv')
df.head(10).to_csv('data-pipeline/data/processed/test_discharge_summaries.csv', index=False)
print('Created test dataset with 10 records')
"
```

Then test with this smaller file:
```bash
python scripts/quick_test_rag.py --hadm-id 130656 --question "What are my diagnoses?" --data-path data-pipeline/data/processed/test_discharge_summaries.csv
```

## Option 2: Test with Existing Embeddings (If Available)

If embeddings were already generated (they're cached), the system will use them:

```bash
python scripts/quick_test_rag.py --hadm-id 130656 --question "What are my diagnoses?"
```

## Option 3: Interactive Mode (Once Embeddings Exist)

Once embeddings are created and cached, use interactive mode:

```bash
python scripts/patient_qa_interactive.py --hadm-id 130656
```

## Understanding the Process

1. **First Run**: Creates embeddings for all chunks (2-5 minutes for full dataset)
   - This can use significant memory
   - Embeddings are cached for future use

2. **Subsequent Runs**: Loads cached embeddings (5-10 seconds)
   - Much faster
   - No memory issues

## If You Get Crashes

The embedding generation might crash on large datasets due to memory. Solutions:

1. **Use smaller dataset** (see Option 1 above)
2. **Wait for process to complete** - embedding generation takes time
3. **Check available memory** - need at least 4-8GB free RAM

## Quick Test Command

Test with a single question on a specific record:

```bash
python scripts/quick_test_rag.py --hadm-id 130656 --question "What are my diagnoses?"
```

## Expected Output

When it works, you'll see:
```
======================================================================
QUICK RAG TEST
======================================================================

📋 HADM ID: 130656
❓ Question: What are my diagnoses?

✅ Found cached embeddings (1 file(s))
   This will load quickly...

📂 Loading RAG system...
   This may take a moment...

✅ RAG System ready!

🔍 Processing question...

======================================================================
ANSWER
======================================================================

[Generated answer based on discharge summary]

📚 Sources: 5 relevant sections found
   Top relevance score: 0.852
======================================================================
```

## Troubleshooting

### Error: Memory Error
- Use smaller test dataset (Option 1)
- Close other applications
- Wait for embeddings to be cached, then use them

### Error: GOOGLE_API_KEY not found
```bash
export GOOGLE_API_KEY="your-api-key"
```

### Error: Missing dependencies
```bash
pip install sentence-transformers faiss-cpu
```

### Process Crashes During Embedding Generation
- This is normal for large datasets
- Use smaller test dataset first
- The embeddings will be cached once generation completes

## Next Steps

1. Start with a small test dataset
2. Verify it works with 10 records
3. Then use the full dataset once embeddings are cached
4. Use interactive mode for natural Q&A






