# Model Development Guide

Complete implementation of Model Development Guidelines with all required components.

## Overview

This guide covers the complete model development lifecycle as specified in the Model Development Guidelines:

1. **Loading Data from Data Pipeline** - Seamless integration with versioned data
2. **Training and Selecting Best Model** - Model training with performance-based selection
3. **Model Validation** - Comprehensive validation with ROUGE and BLEU metrics
4. **Model Bias Detection** - Slicing techniques across demographic groups
5. **Hyperparameter Tuning** - Bayesian optimization with Optuna
6. **Experiment Tracking** - MLflow integration for all experiments
7. **Sensitivity Analysis** - Feature importance and hyperparameter sensitivity
8. **Model Registry** - Version control and reproducibility
9. **CI/CD Pipeline** - Automated training, validation, and bias detection

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
python scripts/setup_gemini_api_key.py
```

### 3. Run Complete Training Pipeline

```bash
python src/training/train_with_tracking.py \
  --data-path data-pipeline/data/processed/processed_discharge_summaries.csv \
  --config configs/gemini_config.json \
  --output-dir models/gemini \
  --enable-tuning \
  --run-name "experiment-1"
```

## Components

### 1. Data Loading from Pipeline

The `CompleteModelTrainer` automatically loads data from the data pipeline with proper train/validation/test splits:

```python
from src.training import CompleteModelTrainer

trainer = CompleteModelTrainer()
train_df, val_df, test_df = trainer.load_data_from_pipeline(
    data_path='data-pipeline/data/processed/processed_discharge_summaries.csv',
    train_split=0.8,
    val_split=0.1
)
```

### 2. Model Training

Training with automatic hyperparameter optimization:

```python
from src.training import CompleteModelTrainer

trainer = CompleteModelTrainer(
    enable_hyperparameter_tuning=True,
    enable_bias_detection=True,
    enable_sensitivity_analysis=True
)

results = trainer.train_and_evaluate(
    data_path='data-pipeline/data/processed/processed_discharge_summaries.csv'
)
```

### 3. Model Validation

Validation with ROUGE and BLEU metrics:

```python
from src.training import ModelValidator

validator = ModelValidator()

# Validate from lists
metrics = validator.validate_model(predictions, references)

# Validate from DataFrame
metrics = validator.validate_from_dataframe(
    df,
    prediction_column='gemini_summary',
    reference_column='cleaned_text'
)

print(f"ROUGE-L F1: {metrics['rougeL_f']:.4f}")
print(f"BLEU: {metrics['bleu']:.4f}")
```

**Metrics Calculated:**
- ROUGE-1 (precision, recall, F1)
- ROUGE-2 (precision, recall, F1)
- ROUGE-L (precision, recall, F1)
- ROUGE-Lsum (precision, recall, F1)
- BLEU score
- Overall score (weighted combination)

### 4. Hyperparameter Tuning

Bayesian optimization using Optuna:

```python
from src.training import HyperparameterTuner

tuner = HyperparameterTuner(
    api_key=os.getenv('GOOGLE_API_KEY'),
    model_name='gemini-2.0-flash-exp',
    n_trials=20
)

study = tuner.optimize(
    train_data=train_df,
    val_data=val_df,
    input_column='cleaned_text',
    reference_column='cleaned_text'
)

best_params = tuner.get_best_hyperparameters(study)
print(f"Best temperature: {best_params['temperature']}")
print(f"Best max_output_tokens: {best_params['max_output_tokens']}")
```

**Hyperparameters Tuned:**
- `temperature`: 0.1 - 1.0 (sampling temperature)
- `max_output_tokens`: 100 - 500 (output length)
- `max_length`: 50 - 200 (summary length)

### 5. Experiment Tracking with MLflow

Automatic experiment tracking:

```python
from src.training import MLflowTracker

with MLflowTracker(experiment_name="gemini-experiments") as tracker:
    # Log hyperparameters
    tracker.log_hyperparameters({
        'temperature': 0.3,
        'max_output_tokens': 2048
    })
    
    # Log metrics
    tracker.log_metrics({
        'rougeL_f': 0.45,
        'bleu': 0.38
    })
    
    # Log model
    tracker.log_model(model)
    
    # Log artifacts
    tracker.log_artifact('bias_report.json')
```

**Tracked Information:**
- Hyperparameters
- Metrics (ROUGE, BLEU, bias scores)
- Model configurations
- Artifacts (reports, plots)
- Tags and metadata

### 6. Model Bias Detection

Bias detection using slicing techniques:

```python
from src.training import ModelBiasDetector

detector = ModelBiasDetector(bias_threshold=0.1)

bias_report = detector.detect_bias(
    df=df_with_predictions,
    prediction_column='gemini_summary',
    reference_column='cleaned_text',
    demographic_columns=['gender', 'ethnicity_clean', 'age_group']
)

print(f"Overall bias score: {bias_report['overall_bias_score']:.4f}")
print(f"Bias alerts: {len(bias_report['bias_alerts'])}")

# Save report
detector.save_bias_report(bias_report, 'logs/bias_report.json')
```

**Slicing Analysis:**
- Performance metrics per demographic group
- Disparity calculations (coefficient of variation, max difference)
- Automatic bias alerts when thresholds exceeded
- Comprehensive bias report with visualizations

### 7. Sensitivity Analysis

Feature importance and hyperparameter sensitivity:

```python
from src.training import SensitivityAnalyzer

analyzer = SensitivityAnalyzer()

# Hyperparameter sensitivity
sensitivity = analyzer.analyze_hyperparameter_sensitivity(
    optimization_history=study_history_df
)

print(f"Most important hyperparameter: {list(sensitivity['hyperparameter_importance'].keys())[0]}")

# Create visualizations
plot_paths = analyzer.create_sensitivity_plots(
    optimization_history=study_history_df,
    output_dir='logs/sensitivity_plots'
)
```

**Analysis Types:**
- Hyperparameter sensitivity (correlation analysis)
- Feature importance (SHAP/LIME for text features)
- Optimization history visualization

### 8. Model Registry

Register models for version control:

```python
from src.training import ModelRegistry

# MLflow Model Registry
registry = ModelRegistry(registry_type='mlflow')
registration = registry.register_model(
    run_id='abc123',
    model_name='gemini-medical-summarization',
    stage='Production'
)

# GCP Artifact Registry
registry_gcp = ModelRegistry(
    registry_type='gcp',
    gcp_project='your-project',
    gcp_location='us-central1',
    gcp_repository='lab-lens-models'
)
registration = registry_gcp.register_model(
    model_path='models/gemini',
    model_version='v1.0.0',
    metadata={'description': 'Best model from experiment 1'}
)
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/model_training_ci.yml`) automatically:

1. **Triggers on code changes** to training code
2. **Runs model training** with validation
3. **Performs bias detection** and checks thresholds
4. **Uploads artifacts** (MLflow runs, models, logs)
5. **Sends notifications** on failures

### Setup CI/CD

1. Add GitHub secret: `GOOGLE_API_KEY`
2. Push code to trigger workflow
3. Check Actions tab for results

### Manual Trigger

```bash
# Trigger workflow manually via GitHub UI or:
gh workflow run model_training_ci.yml
```

## Best Practices

### 1. Data Versioning

Use DVC for data versioning:
```bash
dvc add data-pipeline/data/processed/processed_discharge_summaries.csv
git add data-pipeline/data/processed/processed_discharge_summaries.csv.dvc
```

### 2. Experiment Naming

Use descriptive run names:
```python
run_name = f"experiment-{datetime.now().strftime('%Y%m%d')}-tuning-v1"
```

### 3. Model Selection

Select best model based on validation metrics:
```python
from src.training import get_best_run

best_run = get_best_run(
    experiment_name='gemini-medical-summarization',
    metric='rougeL_f',
    ascending=False  # Higher is better
)
```

### 4. Bias Mitigation

If bias detected:
1. Review bias report
2. Adjust training data (re-sampling, re-weighting)
3. Retrain with bias-aware techniques
4. Re-validate and check bias again

### 5. Hyperparameter Search Space

Adjust search space based on domain knowledge:
```python
# In HyperparameterTuner.objective()
temperature = trial.suggest_float('temperature', 0.1, 0.5, step=0.1)  # Narrower range
```

## Output Structure

```
models/gemini/
├── gemini_config.json          # Model configuration
├── training_results.json       # Training results
├── bias_report.json           # Bias detection report
├── optimization_history.csv    # Hyperparameter tuning history
└── sensitivity_plots/         # Sensitivity analysis plots
    ├── hyperparameter_sensitivity.png
    └── optimization_history.png

mlruns/                        # MLflow tracking
└── gemini-medical-summarization/
    └── runs/
        └── [run_id]/
            ├── metrics/
            ├── params/
            └── artifacts/
```

## Troubleshooting

### Issue: MLflow tracking fails
**Solution:** Ensure `mlruns/` directory is writable or set custom tracking URI

### Issue: Bias detection finds no demographic columns
**Solution:** Check that DataFrame has columns like 'gender', 'ethnicity_clean', 'age_group'

### Issue: Hyperparameter tuning is slow
**Solution:** Reduce `sample_size` parameter or `n_trials` in `HyperparameterTuner`

### Issue: Validation metrics are low
**Solution:** 
- Check data quality
- Adjust hyperparameters
- Try different prompt engineering
- Increase training data

## Next Steps

1. **Production Deployment**: Set up model serving infrastructure
2. **Monitoring**: Implement model performance monitoring
3. **A/B Testing**: Compare model versions in production
4. **Automated Retraining**: Schedule periodic model updates

## References

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Optuna Documentation](https://optuna.readthedocs.io/)
- [Fairlearn Documentation](https://fairlearn.org/)
- [SHAP Documentation](https://shap.readthedocs.io/)






