# Data Pipeline

This directory contains the **single source of truth** for the Lab Lens data pipeline.

It implements an end-to-end pipeline for MIMIC-III discharge note processing:
- Preprocessing (cleaning, de-duplication, demographic standardization)
- Validation (schema + quality checks)
- Feature engineering
- Bias detection
- Automated bias mitigation

## Directory layout

- `scripts/`: pipeline steps + orchestrator
- `tests/`: unit tests for the pipeline steps
- `data/`: pipeline inputs/outputs (raw/processed) *(raw is tracked via DVC pointers)*
- `logs/`: reports and generated plots
- `requirements.txt`: Python dependencies for running this pipeline

## Quick start

### 1) Create and activate a virtualenv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r data_pipeline/requirements.txt
```

### 3) Ensure raw data is available

This repo tracks raw inputs as `.dvc` pointers. Pull data via DVC (if configured) or place the raw file at:

- `data_pipeline/data/raw/mimic_discharge_labs.csv`

## Run the pipeline

Run the full pipeline orchestrator:

```bash
python data_pipeline/scripts/main_pipeline.py
```

Common options (see `--help` for the complete list):

```bash
python data_pipeline/scripts/main_pipeline.py --help
```

## Run tests

```bash
pytest data_pipeline/tests -v
```

## Outputs

Typical outputs include:
- `data_pipeline/data/processed/*`
- `data_pipeline/logs/*.json`
- `data_pipeline/logs/bias_plots/*.png`
