# Prompt Engineering Implementation Details

## Overview

This document explains exactly how prompt engineering is implemented in the Gemini model for medical text summarization.

## Location

**Main Implementation**: `src/training/gemini_model.py` (lines 98-152)

## How It Works

### Step 1: System Prompt (Default Instructions)

The model uses a **system prompt** that defines the role and task:

```python
system_prompt = """You are a medical expert assistant. Your task is to create concise,
accurate summaries of medical discharge summaries. Focus on:
- Chief complaint and primary diagnosis
- Key treatments and procedures
- Discharge medications
- Important follow-up instructions

Keep the summary clear, professional, and medically accurate."""
```

**Purpose**:
- Sets the model's "role" (medical expert assistant)
- Defines the task (summarize discharge summaries)
- Specifies what to include (4 key areas)
- Sets quality expectations (clear, professional, accurate)

### Step 2: User Prompt Construction

The actual prompt sent to Gemini is constructed dynamically:

```python
prompt = f"""{system_prompt}

Please summarize the following medical discharge summary in approximately {max_length} words:

{text}

Summary:"""
```

**Components**:
1. **System prompt** (role and instructions)
2. **Task instruction** (summarize in X words)
3. **Input text** (the medical discharge summary)
4. **Output trigger** ("Summary:")

### Step 3: Full Prompt Example

Here's what gets sent to the API:

```
You are a medical expert assistant. Your task is to create concise,
accurate summaries of medical discharge summaries. Focus on:
- Chief complaint and primary diagnosis
- Key treatments and procedures
- Discharge medications
- Important follow-up instructions

Keep the summary clear, professional, and medically accurate.

Please summarize the following medical discharge summary in approximately 150 words:

Patient admitted with chest pain. History of hypertension and diabetes.
Physical exam shows elevated blood pressure. Discharge diagnosis: Acute
coronary syndrome. Discharge medications: Aspirin 81mg daily, Metformin
500mg twice daily. Follow up with cardiology in 2 weeks.

Summary:
```

### Step 4: API Call

The prompt is sent to Gemini API with generation config:

```python
response = self.model.generate_content(
  prompt,
  generation_config=genai.types.GenerationConfig(
    temperature=self.temperature,   # 0.3 (low = more deterministic)
    max_output_tokens=self.max_output_tokens, # 2048
  )
)
```

## Prompt Engineering Techniques Used

### 1. **Role-Based Prompting**
- "You are a medical expert assistant"
- **Why**: Helps model adopt appropriate persona and knowledge

### 2. **Task Specification**
- "Your task is to create concise, accurate summaries"
- **Why**: Clearly defines what the model should do

### 3. **Structured Output Guidelines**
- Bullet points for what to include:
 - Chief complaint and primary diagnosis
 - Key treatments and procedures
 - Discharge medications
 - Important follow-up instructions
- **Why**: Guides model to include specific information

### 4. **Quality Constraints**
- "Keep the summary clear, professional, and medically accurate"
- **Why**: Sets quality expectations

### 5. **Length Control**
- "approximately {max_length} words"
- **Why**: Controls output length dynamically

### 6. **Output Format Trigger**
- "Summary:" at the end
- **Why**: Signals to model where to start generating

## Customization Options

### Option 1: Custom System Prompt

You can provide a custom system prompt:

```python
custom_prompt = """You are a clinical documentation specialist.
Create brief, structured summaries focusing on:
1. Primary diagnosis
2. Treatment received
3. Discharge plan"""

model.summarize(text, system_prompt=custom_prompt)
```

### Option 2: Few-Shot Examples (Not Currently Active)

The code includes few-shot learning capability (in `train_gemini.py`):

```python
def create_few_shot_examples(self, df: pd.DataFrame, num_examples: int = 3):
  """Creates example pairs to show desired format"""
  examples = []
  for i in range(min(num_examples, len(df))):
    input_text = df.iloc[i]['cleaned_text'][:500]
    summary = # ... extractive summary
    examples.append(f"""
Example {i + 1}:
Input: {input_text[:200]}...
Summary: {summary}
""")
  return '\n'.join(examples)
```

**Status**: Code exists but few-shot examples are not currently injected into prompts.

### Option 3: Configuration-Based Prompts

Prompts can be customized via config file (`configs/gemini_config.json`):

```json
{
 "processing_config": {
  "system_prompt": null, // Can set custom prompt here
  "max_output_length": 150
 }
}
```

## Prompt Engineering Best Practices Applied

### Clear Instructions
- Explicit task definition
- Specific output requirements

### Role Definition
- Model knows it's a "medical expert assistant"

### Structured Guidelines
- Bullet points for clarity
- Specific sections to include

### Quality Constraints
- Professional tone
- Medical accuracy
- Conciseness

### Length Control
- Dynamic word count limits
- Prevents overly long summaries

## Code Flow

```
User calls: model.summarize(text, max_length=150)
  ↓
1. Check if custom system_prompt provided
  ↓
2. Use default system prompt if None
  ↓
3. Construct full prompt:
  - System prompt
  - Task instruction with max_length
  - Input text
  - "Summary:" trigger
  ↓
4. Send to Gemini API with generation config
  ↓
5. Return generated summary
```

## Actual Code Location

**File**: `src/training/gemini_model.py`

**Method**: `GeminiSummarizer.summarize()` (lines 98-152)

**Key Lines**:
- Line 116-124: Default system prompt definition
- Line 126-132: Prompt construction
- Line 136-142: API call with generation config

## Example: Complete Prompt Sent to API

```
You are a medical expert assistant. Your task is to create concise,
accurate summaries of medical discharge summaries. Focus on:
- Chief complaint and primary diagnosis
- Key treatments and procedures
- Discharge medications
- Important follow-up instructions

Keep the summary clear, professional, and medically accurate.

Please summarize the following medical discharge summary in approximately 150 words:

Patient admitted with chest pain. History of hypertension and diabetes.
Physical exam shows elevated blood pressure. Discharge diagnosis: Acute
coronary syndrome. Discharge medications: Aspirin 81mg daily, Metformin
500mg twice daily. Follow up with cardiology in 2 weeks.

Summary:
```

## Improvements You Could Make

### 1. Add Few-Shot Examples
Currently, few-shot examples are generated but not used. You could:

```python
# In summarize() method, add:
few_shot_examples = self.create_few_shot_examples(df, num_examples=3)
prompt = f"""{system_prompt}

{few_shot_examples}

Please summarize the following medical discharge summary...
"""
```

### 2. Chain-of-Thought Prompting
Add reasoning steps:

```python
system_prompt = """... First, identify the chief complaint.
Then, note the primary diagnosis. Next, list key treatments..."""
```

### 3. Output Format Specification
Request structured output:

```python
system_prompt = """... Format your summary as:
**Chief Complaint:** [text]
**Diagnosis:** [text]
**Treatment:** [text]
**Medications:** [text]"""
```

### 4. Domain-Specific Instructions
Add medical terminology guidance:

```python
system_prompt = """... Use standard medical abbreviations
where appropriate. Maintain clinical accuracy..."""
```

## Current Limitations

1. **No few-shot examples in prompts** (code exists but unused)
2. **Fixed prompt structure** (could be more flexible)
3. **No prompt versioning** (can't track prompt changes)
4. **No A/B testing** (can't compare prompt variations)

## Summary

**Prompt Engineering Approach**:
- Role-based system prompt
- Structured output guidelines
- Dynamic length control
- Quality constraints
- ⚠️ Few-shot examples (code exists, not used)
- Chain-of-thought (not implemented)
- Structured output format (not enforced)

**Result**: The model generates good summaries (ROUGE-L: 0.47) using prompt engineering alone, without fine-tuning.






