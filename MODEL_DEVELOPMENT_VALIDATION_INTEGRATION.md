# Model Development & Validation Integration

## Overview

The `test_complete_model.py` script has been enhanced to incorporate **model development** and **model validation** capabilities, making it a comprehensive tool for the complete model lifecycle: development, validation, and testing.

## What's New

### 1. Model Development/Training (`--train`)

You can now train/develop models before testing them. This ensures you're testing with the most up-to-date model configuration.

**Key Features:**
- Loads data from the data pipeline
- Automatically splits data into train/validation/test sets
- Trains the model using the training data
- Saves model configuration and results
- Integrates seamlessly with the testing workflow

**Usage:**
```bash
# Train model, then test
python scripts/test_complete_model.py --train --num-records 20

# Train with custom config
python scripts/test_complete_model.py --train --train-config configs/gemini_config.json --num-records 20

# Train and save to custom directory
python scripts/test_complete_model.py --train --model-dir models/my_experiment --num-records 20
```

### 2. Model Validation (`--validate`)

Integrated model validation using industry-standard metrics (ROUGE and BLEU scores) to quantitatively evaluate model performance.

**Metrics Calculated:**
- **ROUGE-1**: Unigram overlap between generated and reference summaries
- **ROUGE-2**: Bigram overlap
- **ROUGE-L**: Longest common subsequence
- **ROUGE-Lsum**: Sentence-level ROUGE-L
- **BLEU**: Bilingual Evaluation Understudy score
- **Overall Score**: Weighted combination of ROUGE-L F1 and BLEU

**Usage:**
```bash
# Single record with validation
python scripts/test_complete_model.py --index 5 --validate

# Batch testing with validation
python scripts/test_complete_model.py --num-records 10 --validate

# Train, then test with validation
python scripts/test_complete_model.py --train --num-records 20 --validate
```

### 3. Combined Workflow

You can combine training, validation, and testing in a single command:

```bash
# Complete workflow: Train → Validate → Test
python scripts/test_complete_model.py --train --num-records 20 --validate
```

This will:
1. Train/develop the model using the data pipeline
2. Test on the specified number of records
3. Calculate validation metrics (ROUGE/BLEU) for all predictions
4. Save comprehensive results including validation metrics

## Integration Architecture

### Components Used

1. **CompleteModelTrainer** (`src/training/train_with_tracking.py`)
   - Handles model training/development
   - Data loading and splitting
   - Model configuration management

2. **ModelValidator** (`src/training/model_validation.py`)
   - ROUGE score calculation
   - BLEU score calculation
   - Comprehensive validation metrics

3. **CompleteModelTester** (Enhanced in `scripts/test_complete_model.py`)
   - Integrates training and validation
   - Manages the complete testing workflow
   - Saves comprehensive results

## Workflow Examples

### Example 1: Quick Validation Check

```bash
# Test 5 records and validate
python scripts/test_complete_model.py --num-records 5 --validate
```

**Output:**
- Individual test results for each record
- Batch summary statistics
- Validation metrics (ROUGE/BLEU) for all records
- Results saved to `test_results.json`

### Example 2: Model Development Cycle

```bash
# Step 1: Train model
python scripts/test_complete_model.py --train --num-records 20 --validate

# Step 2: Review validation metrics in test_results.json

# Step 3: Adjust config if needed, then retrain

# Step 4: Test on larger batch
python scripts/test_complete_model.py --num-records 100 --validate
```

### Example 3: Specific Record Analysis

```bash
# Test a specific record with validation
python scripts/test_complete_model.py --index 42 --validate

# Or by HADM ID
python scripts/test_complete_model.py --hadm-id 130656 --validate
```

## Output Format

### Enhanced Results Structure

With validation enabled, the results JSON includes:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "num_records": 10,
  "record_results": [...],
  "summary": {
    "total_tested": 10,
    "successful": 9,
    "failed": 1,
    ...
  },
  "validation_metrics": {
    "rouge1_f": 0.4523,
    "rouge2_f": 0.3214,
    "rougeL_f": 0.4456,
    "rougeLsum_f": 0.4456,
    "bleu": 0.3821,
    "overall_score": 0.4256
  }
}
```

## Dependencies

### For Validation

Install validation dependencies:
```bash
pip install rouge-score nltk sacrebleu
```

### For Training

Training uses existing dependencies. Optional dependencies:
- `mlflow` (for experiment tracking - optional)
- `optuna` (for hyperparameter tuning - optional)

## Best Practices

### 1. Development Workflow

1. **Train First**: Use `--train` to develop the model with latest data
2. **Validate**: Use `--validate` to get quantitative metrics
3. **Iterate**: Adjust configuration based on validation metrics
4. **Test**: Test on larger batches once satisfied

### 2. Validation Metrics Interpretation

- **ROUGE-L F1 > 0.4**: Good performance for medical text summarization
- **BLEU > 0.3**: Acceptable quality
- **Overall Score**: Weighted metric - use as primary indicator

### 3. Testing Strategy

- Start small: Test with `--num-records 5` first
- Scale gradually: Increase to 20, 50, 100+ records
- Always validate: Use `--validate` for quantitative assessment
- Monitor costs: Be aware of API usage for Gemini calls

## Comparison: Before vs. After

### Before
- ✅ Testing only (inference)
- ❌ No model development
- ❌ No validation metrics
- ❌ Manual validation required

### After
- ✅ Testing (inference)
- ✅ Model development (`--train`)
- ✅ Validation metrics (`--validate`)
- ✅ Integrated workflow
- ✅ Comprehensive results

## Troubleshooting

### Validation Dependencies Missing

If you see errors about missing validation packages:
```bash
pip install rouge-score nltk sacrebleu
```

### Training Fails

If training fails:
- Check that data file exists at the specified path
- Verify API key is set: `export GOOGLE_API_KEY=your_key`
- Check configuration file format if using `--train-config`

### Low Validation Scores

If validation scores are low:
- Check data quality
- Review model configuration
- Try adjusting hyperparameters
- Consider training on more data

## Next Steps

1. **Experiment Tracking**: Integrate MLflow for experiment tracking
2. **Hyperparameter Tuning**: Enable automatic hyperparameter optimization
3. **Bias Detection**: Add bias detection to validation workflow
4. **Automated Testing**: Set up CI/CD for automated model testing

## Related Documentation

- [MODEL_TESTING_GUIDE.md](MODEL_TESTING_GUIDE.md) - Complete testing guide
- [docs/MODEL_DEVELOPMENT_GUIDE.md](docs/MODEL_DEVELOPMENT_GUIDE.md) - Detailed development guide
- [docs/MODEL_TESTING_GUIDE.md](docs/MODEL_TESTING_GUIDE.md) - Testing best practices



