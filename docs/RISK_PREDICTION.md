# Risk Prediction Module

## Overview

The risk prediction module analyzes medical discharge summaries and predicts patient risk levels based on:
- Medical conditions and diagnoses
- Clinical factors (age, lab results, complexity)
- Discharge summary content
- Demographics and medical history

## Features

### Risk Levels
- **LOW**: Low risk for complications or readmission
- **MEDIUM**: Moderate risk requiring standard follow-up
- **HIGH**: High risk requiring close monitoring

### Risk Factors Analyzed
1. **Age**: Older patients (≥75) have higher risk
2. **Medical Conditions**: High-risk keywords (sepsis, shock, cardiac arrest, etc.)
3. **Abnormal Lab Values**: Number of abnormal laboratory results
4. **Diagnosis Count**: Multiple diagnoses indicate complexity
5. **Clinical Complexity**: Complexity score from discharge summary
6. **Urgency Indicators**: Urgency markers in the summary

## Usage

### Basic Usage (Rule-Based)

```bash
# Predict risk for processed data
python src/training/risk_prediction.py \
  --input data_pipeline/data/processed/processed_discharge_summaries.csv \
  --output models/gemini/risk_predictions.csv \
  --limit 100
```

### Advanced Usage (With Gemini)

```bash
# Use Gemini for more accurate risk prediction
python src/training/risk_prediction.py \
  --input data_pipeline/data/processed/processed_discharge_summaries.csv \
  --output models/gemini/risk_predictions.csv \
  --limit 100 \
  --use-gemini
```

### Integrated Processing (Summarization + Risk)

```bash
# Generate summaries AND predict risk in one step
python scripts/train_with_risk_prediction.py \
  --input data_pipeline/data/processed/processed_discharge_summaries.csv \
  --output models/gemini/summaries_with_risk.csv \
  --limit 100
```

## Output Format

The output CSV contains:
- `hadm_id`: Hospital admission ID
- `subject_id`: Patient ID
- `risk_level`: LOW, MEDIUM, or HIGH
- `risk_score`: Numerical score (0.0 to 1.0)
- `risk_factor_*`: Individual risk factor values
 - `risk_factor_age`
 - `risk_factor_abnormal_labs`
 - `risk_factor_diagnosis_count`
 - `risk_factor_high_risk_keywords`
 - `risk_factor_complexity_score`
 - etc.

## Risk Prediction Methods

### 1. Rule-Based (Default)
- Fast and deterministic
- Based on clinical risk factors
- No API calls required
- Good for batch processing

### 2. Gemini-Based (Optional)
- More nuanced analysis
- Considers context and medical knowledge
- Requires API calls (slower, costs)
- Better for complex cases

## Risk Scoring

Risk scores are calculated from:
- Age risk: 0-0.3 points
- Condition risk: 0-0.4 points
- Lab risk: 0-0.2 points
- Diagnosis risk: 0-0.15 points
- Complexity/Urgency: 0-0.2 points

**Total Score Range**: 0.0 to 1.0

**Risk Levels**:
- LOW: Score < 0.4
- MEDIUM: Score 0.4 - 0.7
- HIGH: Score ≥ 0.7

## High-Risk Conditions

The system identifies high-risk conditions including:
- Sepsis, shock, cardiac arrest
- Stroke, myocardial infarction
- Respiratory/renal/liver failure
- ICU admission, ventilator use
- Major surgery, complications
- Severe infections, bleeding

## Integration with Pipeline

The risk prediction module integrates with:
1. **Data Preprocessing**: Uses processed discharge summaries
2. **Summarization**: Can be combined with summary generation
3. **Model Training**: Can be used for model evaluation
4. **Clinical Decision Support**: Provides risk scores for care planning

## Example

```python
from src.training.risk_prediction import MedicalRiskPredictor

# Initialize predictor
predictor = MedicalRiskPredictor(use_gemini=False)

# Predict risk for a record
result = predictor.predict(record)

print(f"Risk Level: {result['risk_level']}")
print(f"Risk Score: {result['risk_score']}")
print(f"Risk Factors: {result['risk_factors']}")
```

## Performance

- **Rule-Based**: ~1000 records/second
- **Gemini-Based**: ~1 record/second (due to API rate limits)

## Use Cases

1. **Readmission Risk**: Predict likelihood of hospital readmission
2. **Complication Risk**: Identify patients at risk for complications
3. **Care Planning**: Guide follow-up care intensity
4. **Resource Allocation**: Prioritize high-risk patients
5. **Clinical Research**: Analyze risk factors in patient populations

## Future Enhancements

- Machine learning model training on historical outcomes
- Integration with EHR systems
- Real-time risk prediction
- Custom risk models for specific conditions
- Risk trend analysis over time




