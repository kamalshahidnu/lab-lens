# RAG System Testing Guide

This guide shows you how to test the RAG system with specific discharge summary records.

## Quick Start

### Step 1: List Available Records

First, see what records are available:

```bash
python scripts/test_rag_with_record.py --list-records
```

This will show you available HADM IDs (hospital admission IDs) from your processed discharge summaries.

### Step 2: View a Specific Record

Before asking questions, you can view the discharge summary:

```bash
python scripts/test_rag_with_record.py --view-record 130656
```

This shows:
- Patient information (age, gender, subject ID)
- Preview of the discharge summary text
- Diagnoses (if available)
- Medications (if available)

### Step 3: Test RAG with Questions

Test the RAG system with a specific record using default questions:

```bash
python scripts/test_rag_with_record.py --test 130656
```

This will ask 5 default questions:
1. "What are my diagnoses?"
2. "What medications do I need to take?"
3. "What happened during my hospital stay?"
4. "What are my discharge instructions?"
5. "When is my follow-up appointment?"

### Step 4: Test with Custom Questions

Ask your own questions:

```bash
python scripts/test_rag_with_record.py --test 130656 \
  --questions "What are my diagnoses?" "What medications do I need?" "What should I watch for?"
```

## Complete Example Workflow

```bash
# 1. List available records
python scripts/test_rag_with_record.py --list-records

# 2. View a specific record to understand what's in it
python scripts/test_rag_with_record.py --view-record 130656

# 3. Test RAG with that record
python scripts/test_rag_with_record.py --test 130656

# 4. Ask custom questions
python scripts/test_rag_with_record.py --test 130656 \
  --questions "What are my diagnoses?" "What medications do I need?"
```

## Interactive Mode

You can also use the interactive mode for a more natural Q&A session:

```bash
# Interactive mode with a specific patient
python scripts/patient_qa_interactive.py --hadm-id 130656
```

This allows you to:
- Ask questions interactively
- Type 'help' for example questions
- Type 'summary' to see patient record summary
- Type 'exit' to quit

## Example Questions You Can Ask

- **Diagnoses**: "What are my diagnoses?" / "What conditions do I have?"
- **Medications**: "What medications do I need to take?" / "What are my discharge medications?"
- **Follow-up**: "When is my follow-up appointment?" / "Do I need a follow-up?"
- **Hospital Stay**: "What happened during my hospital stay?" / "What was my hospital course?"
- **Instructions**: "What are my discharge instructions?" / "What should I do at home?"
- **Symptoms**: "What should I watch for?" / "What are warning signs?"
- **Explanations**: "Can you explain my condition in simple terms?"

## Expected Output

When you run the test, you'll see:

1. **System initialization** - Loading data and creating embeddings (first run takes a few minutes)
2. **Questions and Answers** - Each question will show:
   - The question asked
   - The generated answer
   - Source citations (relevant sections found)
   - Relevance scores

Example output:
```
──────────────────────────────────────────────────────
QUESTION 1: What are my diagnoses?
──────────────────────────────────────────────────────

📝 Answer:
Based on your discharge summary, your primary diagnoses include...

📚 Sources: 5 relevant sections found
   Top source relevance score: 0.852
```

## Troubleshooting

### Error: No record found
- Verify the HADM ID exists using `--list-records`
- HADM IDs are numeric (e.g., 130656)

### Error: Missing dependencies
```bash
pip install sentence-transformers faiss-cpu
```

### Error: GOOGLE_API_KEY not found
```bash
export GOOGLE_API_KEY="your-api-key"
# Or
python scripts/setup_gemini_api_key.py
```

### First Run is Slow
- First run creates embeddings (2-5 minutes for large datasets)
- Subsequent runs load cached embeddings (5-10 seconds)

## Alternative: Direct Python API

You can also use the RAG system programmatically:

```python
from src.rag.patient_qa import PatientQA

# Initialize
qa = PatientQA(data_path="data-pipeline/data/processed/processed_discharge_summaries.csv")

# View record summary
summary = qa.get_record_summary(130656)
print(summary)

# Ask a question
result = qa.ask_question("What are my diagnoses?", hadm_id=130656)
print(result['answer'])
print(f"Sources: {len(result['sources'])} sections found")
```

## Tips for Better Results

1. **Be Specific**: More specific questions get better answers
   - ✅ "What medications do I need to take?"
   - ❌ "meds?"

2. **Use Patient Context**: Always specify HADM ID for patient-specific questions
   - ✅ `--test 130656`
   - ❌ General questions without HADM ID may get mixed results

3. **View Record First**: Understand what's in the summary before asking questions

4. **Multiple Questions**: Ask follow-up questions to explore different aspects

## Next Steps

- Try different HADM IDs from your dataset
- Experiment with various question types
- Compare answers across different records
- Use interactive mode for natural conversations

Happy testing! 🚀






