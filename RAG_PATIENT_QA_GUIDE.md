# RAG-Based Patient Q&A Guide

## Overview

The RAG (Retrieval-Augmented Generation) system enables patients to ask questions about their discharge summaries. The system:

1. **Retrieves** relevant information from discharge summaries using semantic search
2. **Generates** patient-friendly answers using Gemini AI
3. **Provides** source citations so patients can see where answers come from

## Features

- ✅ **Semantic Search**: Finds relevant sections in discharge summaries using embeddings
- ✅ **Context-Aware Answers**: Uses retrieved context to generate accurate answers
- ✅ **Patient-Friendly**: Answers in simple, understandable language
- ✅ **Source Citations**: Shows which sections of the report were used
- ✅ **Multi-Question Support**: Answer multiple questions at once
- ✅ **Patient Filtering**: Filter questions to specific patient records

## Quick Start

### Installation

Install required dependencies:

```bash
pip install sentence-transformers faiss-cpu
```

**Note**: `faiss-cpu` is optional but recommended for faster similarity search. The system will work without it using numpy-based search (slower).

### Basic Usage

#### Interactive Mode (Recommended)

Start an interactive Q&A session:

```bash
python scripts/patient_qa_interactive.py
```

For a specific patient:

```bash
python scripts/patient_qa_interactive.py --hadm-id 130656
```

#### Single Question

Answer a single question:

```bash
python scripts/patient_qa_interactive.py --question "What are my diagnoses?"
```

For a specific patient:

```bash
python scripts/patient_qa_interactive.py --hadm-id 130656 --question "What medications do I need to take?"
```

#### Multiple Questions

Answer multiple questions at once:

```bash
python scripts/patient_qa_interactive.py --questions \
  "What are my diagnoses?" \
  "What medications do I need?" \
  "When is my follow-up?"
```

## Example Questions

Patients can ask questions like:

- **Diagnoses**: "What are my diagnoses?" / "What conditions do I have?"
- **Medications**: "What medications do I need to take?" / "What are my discharge medications?"
- **Follow-up**: "When is my follow-up appointment?" / "Do I need a follow-up?"
- **Lab Results**: "What were my lab results?" / "Were there any abnormal labs?"
- **Hospital Stay**: "What happened during my hospital stay?" / "What was my hospital course?"
- **Instructions**: "What are my discharge instructions?" / "What should I do at home?"
- **Symptoms**: "What should I watch for?" / "What are warning signs I should look for?"
- **Explanations**: "Can you explain my condition in simple terms?" / "What does this diagnosis mean?"

## How It Works

### 1. Document Processing

- Discharge summaries are split into chunks (500 characters with 50 character overlap)
- Each chunk is embedded using a sentence transformer model
- Embeddings are stored in a vector database (FAISS or numpy-based)

### 2. Question Processing

- Patient's question is embedded using the same model
- Semantic similarity search finds the most relevant chunks
- Top K chunks (default: 5) are retrieved

### 3. Answer Generation

- Retrieved chunks are provided as context to Gemini
- Gemini generates a patient-friendly answer based on the context
- Answer is returned with source citations

## Architecture

```
Patient Question
      ↓
  Embedding Model
      ↓
  Vector Search (FAISS/numpy)
      ↓
  Retrieve Relevant Chunks
      ↓
  Build Context
      ↓
  Gemini AI (Answer Generation)
      ↓
  Patient-Friendly Answer
```

## Advanced Usage

### Python API

Use the RAG system programmatically:

```python
from src.rag.patient_qa import PatientQA

# Initialize system
qa = PatientQA(
    data_path="data-pipeline/data/processed/processed_discharge_summaries.csv"
)

# Ask a question
result = qa.ask_question(
    question="What are my diagnoses?",
    hadm_id=130656  # Optional: filter to specific patient
)

print(result['answer'])
print(f"Sources: {len(result['sources'])}")
```

### Custom Configuration

```python
from src.rag.patient_qa import PatientQA

qa = PatientQA(
    data_path="path/to/data.csv",
    embedding_model="all-mpnet-base-v2",  # Different embedding model
    gemini_model="gemini-1.5-pro",        # Different Gemini model
    rag_k=10  # Retrieve more chunks for context
)
```

### Direct RAG System Access

```python
from src.rag.rag_system import RAGSystem

# Initialize RAG system
rag = RAGSystem(
    embedding_model="all-MiniLM-L6-v2",
    chunk_size=500,
    chunk_overlap=50,
    data_path="data-pipeline/data/processed/processed_discharge_summaries.csv"
)

# Retrieve relevant chunks
results = rag.retrieve(
    query="What medications are prescribed?",
    k=5,
    hadm_id_filter=130656,  # Optional: filter by HADM ID
    min_score=0.3  # Minimum similarity threshold
)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Chunk: {result['chunk'][:100]}...")
```

## Configuration Options

### Embedding Models

Available sentence transformer models:

- `all-MiniLM-L6-v2` (default) - Fast, good quality, 384 dimensions
- `all-mpnet-base-v2` - Better quality, slower, 768 dimensions
- `all-MiniLM-L12-v2` - Balanced option

Install additional models:
```bash
# Models are downloaded automatically on first use
# No manual installation needed
```

### Chunking Strategy

Default settings:
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters

Adjust in `RAGSystem`:
```python
rag = RAGSystem(
    chunk_size=750,      # Larger chunks
    chunk_overlap=100    # More overlap
)
```

### Retrieval Parameters

```python
results = rag.retrieve(
    query="question",
    k=10,                # Number of chunks to retrieve
    min_score=0.4,       # Minimum similarity score (0-1)
    hadm_id_filter=123   # Filter to specific patient
)
```

## Caching

Embeddings are automatically cached to speed up subsequent runs:

- **Cache Location**: `models/rag_embeddings/embeddings_{filename}.pkl`
- **First Run**: Creates embeddings (takes a few minutes)
- **Subsequent Runs**: Loads from cache (seconds)

To rebuild embeddings:
```python
rag.load_data("data.csv", force_rebuild=True)
```

## Output Format

### Answer Dictionary

```python
{
    'answer': 'Patient-friendly answer...',
    'question': 'Original question',
    'sources': [
        {
            'chunk': 'Relevant text excerpt...',
            'score': 0.85,  # Similarity score (0-1)
            'hadm_id': 130656,
            'metadata': {...}
        },
        ...
    ],
    'num_sources': 5,
    'hadm_id': 130656,
    'timestamp': '2024-01-01T12:00:00'
}
```

## Performance

### Speed

- **Embedding Generation** (first run): ~2-5 minutes for 300K records
- **Embedding Loading** (cached): ~5-10 seconds
- **Question Answering**: ~2-5 seconds per question

### Accuracy

- Semantic search finds relevant sections even with different wording
- Gemini generates contextually accurate answers
- Source citations help verify accuracy

## Troubleshooting

### Import Errors

**Error**: `No module named 'sentence_transformers'`

**Solution**:
```bash
pip install sentence-transformers
```

### FAISS Not Available

**Warning**: `faiss-cpu not available. Using numpy-based similarity search.`

**Solution** (optional but recommended):
```bash
pip install faiss-cpu
```

**Note**: System works without FAISS, but search will be slower.

### Embedding Model Download

Models are downloaded automatically on first use. First initialization may take 1-2 minutes.

### Memory Issues

For very large datasets:

1. Use smaller chunk sizes
2. Use CPU-only FAISS: `pip install faiss-cpu` (instead of `faiss-gpu`)
3. Process in batches

### Gemini API Errors

**Error**: `GOOGLE_API_KEY not found`

**Solution**:
```bash
export GOOGLE_API_KEY="your-api-key"
# Or
python scripts/setup_gemini_api_key.py
```

## Best Practices

### 1. Patient-Specific Questions

Always use `--hadm-id` when asking about a specific patient:

```bash
python scripts/patient_qa_interactive.py --hadm-id 130656
```

### 2. Clear Questions

Encourage patients to ask clear, specific questions:
- ✅ "What are my discharge medications?"
- ❌ "meds?"

### 3. Multiple Follow-ups

Use interactive mode for natural conversation:

```bash
python scripts/patient_qa_interactive.py --hadm-id 130656
```

### 4. Verify Sources

Always check source citations to verify answers come from the report.

## Integration Examples

### Flask API Integration

```python
from flask import Flask, request, jsonify
from src.rag.patient_qa import PatientQA

app = Flask(__name__)
qa_system = PatientQA()

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    hadm_id = data.get('hadm_id')
    
    result = qa_system.ask_question(question, hadm_id=hadm_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
```

### Batch Processing

```python
from src.rag.patient_qa import PatientQA

qa = PatientQA()

questions = [
    "What are my diagnoses?",
    "What medications do I need?",
    "When is my follow-up?"
]

results = qa.ask_multiple_questions(questions, hadm_id=130656)

for question, result in zip(questions, results):
    print(f"Q: {question}")
    print(f"A: {result['answer']}\n")
```

## Future Enhancements

Planned improvements:

- [ ] Support for follow-up questions (conversation context)
- [ ] Multi-language support
- [ ] Audio input/output
- [ ] Integration with patient portals
- [ ] Feedback mechanism for answer quality
- [ ] Visualization of retrieved sections
- [ ] Support for image-based questions

## Related Documentation

- [MODEL_TESTING_GUIDE.md](MODEL_TESTING_GUIDE.md) - Model testing
- [docs/MODEL_DEVELOPMENT_GUIDE.md](docs/MODEL_DEVELOPMENT_GUIDE.md) - Model development

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review error messages carefully
3. Verify data file path and format
4. Check API keys are set correctly



