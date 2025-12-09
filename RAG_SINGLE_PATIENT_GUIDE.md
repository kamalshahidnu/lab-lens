# Single Patient RAG Q&A Guide

## Overview

The RAG system now supports **single-patient mode** - loading and processing only one patient's discharge summary for efficient Q&A sessions. This is the recommended approach for patient-facing applications.

## Key Benefits

✅ **Fast**: Only processes one patient's record (typically 50-200 chunks vs 60,000+)  
✅ **Memory Efficient**: Uses minimal RAM  
✅ **Secure**: Only loads the specific patient's data  
✅ **Simple**: No need to filter - all questions are about the same patient  

## Quick Start

### For a Specific Patient (Recommended)

```bash
# Interactive Q&A for patient with HADM ID 130656
python scripts/patient_qa_single.py --hadm-id 130656
```

This will:
- Load ONLY that patient's discharge summary
- Create embeddings for just that record
- Answer questions based solely on that patient's report

### Single Question

```bash
python scripts/patient_qa_single.py \
  --hadm-id 130656 \
  --question "What are my diagnoses?"
```

### View Record First

```bash
python scripts/patient_qa_single.py \
  --hadm-id 130656 \
  --view
```

## How It Works

### Single-Patient Mode

When you specify `--hadm-id`:
1. **Loads only that patient's record** from the CSV
2. **Creates embeddings** for just that patient's chunks (typically 50-200)
3. **Answers questions** using only that patient's discharge summary
4. **Caches embeddings** separately per patient

### Comparison

| Mode | Records Loaded | Chunks Created | Memory Usage | Speed |
|------|---------------|----------------|--------------|-------|
| **All Records** | 967 | ~62,000 | High (2-4 GB) | Slow (2-5 min) |
| **Single Patient** | 1 | ~50-200 | Low (<100 MB) | Fast (5-10 sec) |

## Usage Examples

### Interactive Mode (Best for Testing)

```bash
python scripts/patient_qa_single.py --hadm-id 130656
```

Then ask questions like:
- "What are my diagnoses?"
- "What medications do I need to take?"
- "What happened during my hospital stay?"
- "What should I watch for at home?"

### Programmatic Use

```python
from src.rag.patient_qa import PatientQA

# Initialize with single patient
qa = PatientQA(
    data_path="data-pipeline/data/processed/processed_discharge_summaries.csv",
    hadm_id=130656  # Only loads this patient's record
)

# Ask questions (no need to specify hadm_id again)
result = qa.ask_question("What are my diagnoses?")
print(result['answer'])

result = qa.ask_question("What medications do I need?")
print(result['answer'])
```

## Caching

Embeddings are cached separately per patient:
- **Cache location**: `models/rag_embeddings/embeddings_processed_discharge_summaries_130656.pkl`
- **First run**: Creates embeddings (5-10 seconds for one patient)
- **Subsequent runs**: Loads from cache (1-2 seconds)

## Finding Patient HADM IDs

List available records:

```bash
python scripts/test_rag_with_record.py --list-records
```

Or use Python:

```python
import pandas as pd
df = pd.read_csv('data-pipeline/data/processed/processed_discharge_summaries.csv')
print(df[['hadm_id', 'subject_id']].head(10))
```

## Workflow for Patient Q&A

### Step 1: Patient provides HADM ID

When a patient wants to ask questions about their discharge summary, they provide their HADM ID.

### Step 2: Load their record

```bash
python scripts/patient_qa_single.py --hadm-id <their_hadm_id>
```

### Step 3: Answer questions

The system answers questions based ONLY on that patient's discharge summary.

## API Integration Example

For a web application, you could do:

```python
from flask import Flask, request, jsonify
from src.rag.patient_qa import PatientQA

app = Flask(__name__)
qa_systems = {}  # Cache Q&A systems per patient

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    hadm_id = data.get('hadm_id')
    question = data.get('question')
    
    # Initialize or reuse Q&A system for this patient
    if hadm_id not in qa_systems:
        qa_systems[hadm_id] = PatientQA(
            data_path="data-pipeline/data/processed/processed_discharge_summaries.csv",
            hadm_id=hadm_id  # Single-patient mode
        )
    
    # Ask question
    result = qa_systems[hadm_id].ask_question(question)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
```

## Security & Privacy

- ✅ Only loads the specific patient's data
- ✅ No cross-patient data leakage
- ✅ Embeddings cached separately per patient
- ✅ Answers based only on that patient's report

## Performance

- **First run** (create embeddings): 5-10 seconds
- **Subsequent runs** (cached): 1-2 seconds  
- **Question answering**: 2-5 seconds per question
- **Memory usage**: <100 MB (vs 2-4 GB for all records)

## Troubleshooting

### Error: No record found with HADM ID

Verify the HADM ID exists:
```bash
python -c "import pandas as pd; df = pd.read_csv('data-pipeline/data/processed/processed_discharge_summaries.csv'); print(df[df['hadm_id'] == 130656])"
```

### Still Slow?

Even in single-patient mode, first run creates embeddings. Subsequent runs use cache and are much faster.

### Memory Issues

If you still have memory issues, you might have other processes running. Single-patient mode uses minimal memory.

## Comparison with Previous Approach

### Before (All Records)
```python
qa = PatientQA(data_path="...")  # Loads ALL 967 records
result = qa.ask_question("What are my diagnoses?", hadm_id=130656)  # Filters at query time
```

### Now (Single Patient) ✅
```python
qa = PatientQA(data_path="...", hadm_id=130656)  # Loads ONLY this patient
result = qa.ask_question("What are my diagnoses?")  # No filter needed
```

## Summary

Single-patient mode is:
- ✅ **Faster** - processes only one record
- ✅ **More efficient** - minimal memory usage
- ✅ **More secure** - only loads that patient's data
- ✅ **Simpler** - no need to filter at query time

**Use this mode for patient-facing Q&A applications!**






