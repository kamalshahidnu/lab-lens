# Model Testing Guide

This guide explains how to test, develop, and validate the medical models with different data configurations.

## Features

- **Testing**: Test models on single or multiple records
- **Model Development**: Train/develop models before testing
- **Model Validation**: Validate model performance with ROUGE/BLEU metrics
- **Batch Processing**: Test multiple records with aggregate statistics

## Quick Start

### Test First N Records

To test the model on the first n records from your processed data:

```bash
# Test first 5 records
python scripts/test_complete_model.py --num-records 5

# Test first 10 records with validation metrics
python scripts/test_complete_model.py --num-records 10 --validate

# Test first 50 records
python scripts/test_complete_model.py --num-records 50
```

### Test with Model Development

To train/develop a model before testing:

```bash
# Train model, then test first 20 records with validation
python scripts/test_complete_model.py --train --num-records 20 --validate
```

### Test a Specific Record

To test a specific record:

```bash
# Test record at index 5 (0-based indexing)
python scripts/test_complete_model.py --index 5

# Test record with specific HADM ID
python scripts/test_complete_model.py --hadm-id 130656

# Test first record (default)
python scripts/test_complete_model.py
```

## Testing Modes

### 1. Single Record Testing

Tests one record at a time with detailed output:

```bash
# By index
python scripts/test_complete_model.py --index 10

# By HADM ID
python scripts/test_complete_model.py --hadm-id 130656

# First record (default)
python scripts/test_complete_model.py

# With validation metrics
python scripts/test_complete_model.py --index 10 --validate
```

**Output**: 
- Detailed test results for discharge summary generation
- Risk prediction results with factors and recommendations
- Optional validation metrics (ROUGE/BLEU) if `--validate` is used
- Results saved to `test_results.json`

### 2. Batch Testing (First N Records)

Tests multiple records sequentially and provides aggregate statistics:

```bash
# Test first 5 records
python scripts/test_complete_model.py --num-records 5
```

**Output**:
- Individual test results for each record
- Batch summary with pass/fail counts
- Success rate statistics
- All results saved to `test_results.json`

### 3. Sample Data Testing

Test with hardcoded sample data (useful for quick testing without data files):

```bash
python scripts/test_complete_model.py --use-sample
```

### 4. Model Development/Training

Train or develop models before testing (optional):

```bash
# Train model and then test
python scripts/test_complete_model.py --train --num-records 20

# Train with custom config and validate
python scripts/test_complete_model.py --train --train-config configs/gemini_config.json --num-records 20 --validate

# Train and save to custom directory
python scripts/test_complete_model.py --train --model-dir models/my_experiment --num-records 20
```

**What happens during training:**
- Loads data from the processed CSV file
- Splits data into train/validation/test sets
- Trains/develops the model using the training data
- Validates on validation set
- Saves model configuration and results to the model directory
- Then proceeds with testing as requested

**Note**: Training is optional. If you skip `--train`, the script uses the existing model for inference.

## Advanced Options

### Custom Data Path

```bash
python scripts/test_complete_model.py --data-path /path/to/your/data.csv --num-records 5
```

### Override Patient Info

```bash
# Override age and gender for a specific record
python scripts/test_complete_model.py --index 0 --age 70 --gender F
```

### Custom Output File

```bash
# Save results to a custom file
python scripts/test_complete_model.py --num-records 5 --output my_test_results.json
```

### Model Validation

Enable validation metrics (ROUGE/BLEU scores) to evaluate model performance:

```bash
# Single record with validation
python scripts/test_complete_model.py --index 5 --validate

# Batch testing with validation
python scripts/test_complete_model.py --num-records 10 --validate

# Train, then test with validation
python scripts/test_complete_model.py --train --num-records 20 --validate
```

**Validation Metrics Calculated:**
- **ROUGE-1**: Unigram overlap (precision, recall, F1)
- **ROUGE-2**: Bigram overlap (precision, recall, F1)
- **ROUGE-L**: Longest common subsequence (precision, recall, F1)
- **ROUGE-Lsum**: Sentence-level ROUGE-L (precision, recall, F1)
- **BLEU**: Bilingual Evaluation Understudy score
- **Overall Score**: Weighted combination of ROUGE-L F1 and BLEU

**Requirements**: 
- Install validation dependencies: `pip install rouge-score nltk`
- The `--validate` flag enables these metrics

## Output Format

### Single Record Output

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "discharge_summary_test": {
    "status": "success",
    "summary": "...",
    "summary_length": 150
  },
  "risk_prediction_test": {
    "status": "success",
    "risk_level": "MEDIUM",
    "risk_score": 65,
    "risk_factors": {...}
  },
  "overall_status": "success"
}
```

### Batch Testing Output

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "num_records": 5,
  "record_results": [
    {
      "record_index": 0,
      "hadm_id": 130656,
      "discharge_summary_test": {...},
      "risk_prediction_test": {...},
      "overall_status": "success"
    },
    ...
  ],
  "summary": {
    "total_tested": 5,
    "successful": 4,
    "failed": 1,
    "discharge_summary_success": 5,
    "risk_prediction_success": 4
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

## Examples

### Example 1: Quick Test with First 3 Records

```bash
python scripts/test_complete_model.py --num-records 3
```

This will:
1. Load the first 3 records from the processed data
2. Test each record for discharge summary generation
3. Test each record for risk prediction
4. Display individual results and summary statistics
5. Save all results to `test_results.json`

### Example 2: Test Specific Record by Index

```bash
python scripts/test_complete_model.py --index 42
```

This will:
1. Load record at index 42 (0-based)
2. Display detailed test results
3. Save results to `test_results.json`

### Example 3: Test Specific Record by HADM ID

```bash
python scripts/test_complete_model.py --hadm-id 149188
```

This will:
1. Find and load the record with HADM ID 149188
2. Display detailed test results
3. Save results to `test_results.json`

### Example 4: Train Model and Test with Validation

```bash
python scripts/test_complete_model.py --train --num-records 20 --validate
```

This will:
1. Train/develop the model using the data pipeline
2. Split data into train/validation/test sets
3. Save model configuration to `models/gemini/`
4. Test the first 20 records
5. Calculate and display ROUGE/BLEU validation metrics
6. Save all results including validation metrics to `test_results.json`

### Example 5: Test with Validation Metrics Only

```bash
python scripts/test_complete_model.py --num-records 10 --validate
```

This will:
1. Test the first 10 records
2. Calculate ROUGE/BLEU metrics comparing summaries to original text
3. Display validation metrics in console and save to results file

## Tips

1. **Start Small**: Begin with `--num-records 1` or `--num-records 3` to verify everything works before testing larger batches.

2. **Monitor API Usage**: When testing many records, be aware of API rate limits and costs for Gemini API calls.

3. **Review Results**: Check the JSON output file for detailed results, especially for batch testing where console output may be truncated.

4. **Use Indexes**: If you know the index of a record you want to test, use `--index` for faster lookups than searching by HADM ID.

5. **Enable Validation**: Use `--validate` flag to get quantitative metrics (ROUGE/BLEU) that help evaluate model performance objectively.

6. **Train Before Testing**: Use `--train` flag if you want to develop/train the model with latest data before testing. This ensures you're testing with the most up-to-date model configuration.

7. **Model Development Workflow**: 
   - Train: `python scripts/test_complete_model.py --train --num-records 20 --validate`
   - Check validation metrics in results
   - Iterate on model configuration if needed
   - Test on larger batches once satisfied

8. **Validation Dependencies**: If you see errors about missing validation packages, install them:
   ```bash
   pip install rouge-score nltk sacrebleu
   ```

## Troubleshooting

### File Not Found

If you get a warning about the data file not found:
- Check that `data-pipeline/data/processed/processed_discharge_summaries.csv` exists
- Or specify the path with `--data-path /path/to/your/file.csv`

### Index Out of Range

If you specify an index that doesn't exist, the script will use the first record as a fallback.

### HADM ID Not Found

If the HADM ID you specify doesn't exist, the script will use the first record as a fallback.

