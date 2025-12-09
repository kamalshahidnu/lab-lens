# RAG Single-Patient Mode - Usage Guide

## Overview

The RAG system now supports **single-patient mode**, loading only one patient's discharge summary instead of all records. This is the recommended approach for patient Q&A applications.

## Quick Start

### Interactive Q&A for One Patient

```bash
python scripts/patient_qa_single.py --hadm-id 130656
```

This loads ONLY that patient's record and allows interactive Q&A.

### Single Question

```bash
python scripts/patient_qa_single.py \
  --hadm-id 130656 \
  --question "What are my diagnoses?"
```

## How Single-Patient Mode Works

### Before (All Records) ❌
- Loads all 967 records
- Creates 62,354 chunks
- Uses 2-4 GB memory
- Takes 2-5 minutes

### Now (Single Patient) ✅
- Loads only 1 record
- Creates ~50-200 chunks
- Uses <100 MB memory
- Takes 5-10 seconds

## Benefits

1. **Fast**: Only processes one patient's record
2. **Efficient**: Minimal memory usage
3. **Secure**: Only loads that patient's data
4. **Simple**: No filtering needed - all data is from that patient

## Usage

### Command Line

```bash
# Interactive mode (recommended)
python scripts/patient_qa_single.py --hadm-id 130656

# View record first
python scripts/patient_qa_single.py --hadm-id 130656 --view

# Single question
python scripts/patient_qa_single.py --hadm-id 130656 --question "What are my diagnoses?"
```

### Python API

```python
from src.rag.patient_qa import PatientQA

# Initialize with single patient (only loads that patient's data)
qa = PatientQA(
    data_path="data-pipeline/data/processed/processed_discharge_summaries.csv",
    hadm_id=130656  # Single-patient mode
)

# Ask questions (no hadm_id needed - already filtered)
result = qa.ask_question("What are my diagnoses?")
print(result['answer'])

result = qa.ask_question("What medications do I need?")
print(result['answer'])
```

## Key Changes

### RAGSystem
- Added `hadm_id` parameter to `__init__()`
- Filters data to single patient before creating embeddings
- Separate cache files per patient

### PatientQA
- Added `hadm_id` parameter to `__init__()`
- Loads only that patient's data
- No need to filter at query time

## Files Modified

1. ✅ `src/rag/rag_system.py` - Added single-patient filtering
2. ✅ `src/rag/patient_qa.py` - Added single-patient mode support
3. ✅ `scripts/patient_qa_single.py` - New script for single-patient Q&A

## Example Workflow

1. **Patient provides HADM ID**: `130656`
2. **Load their record only**: System filters CSV to just that patient
3. **Create embeddings**: Only for that patient's chunks (~50-200 chunks)
4. **Answer questions**: All based on that patient's report

## Performance

- **First run**: 5-10 seconds (create embeddings for one patient)
- **Subsequent runs**: 1-2 seconds (load cached embeddings)
- **Memory**: <100 MB (vs 2-4 GB for all records)

## Try It Now!

```bash
python scripts/patient_qa_single.py --hadm-id 130656
```

This will load only patient 130656's discharge summary and let you ask questions interactively!






