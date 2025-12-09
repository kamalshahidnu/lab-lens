# Lab Lens Project Structure

This document describes the standard open-source project structure of Lab Lens.

## Directory Structure

```
lab-lens/
├── .github/                    # GitHub configuration
│   ├── workflows/             # CI/CD pipelines
│   │   └── model_training_ci.yml
│   └── ISSUE_TEMPLATE/        # Issue templates
│       ├── bug_report.md
│       └── feature_request.md
│
├── src/                       # Source code
│   ├── __init__.py
│   ├── training/              # Model training modules
│   │   ├── __init__.py
│   │   ├── gemini_model.py
│   │   ├── train_gemini.py
│   │   ├── gemini_inference.py
│   │   ├── mlflow_tracking.py
│   │   ├── model_validation.py
│   │   ├── hyperparameter_tuning.py
│   │   ├── model_bias_detection.py
│   │   ├── sensitivity_analysis.py
│   │   ├── model_registry.py
│   │   ├── model_rollback.py
│   │   ├── risk_prediction.py
│   │   ├── medical_image_analysis.py
│   │   ├── train_with_tracking.py
│   │   ├── example_usage.py
│   │   └── README.md
│   ├── utils/                 # Utility modules
│   │   ├── __init__.py
│   │   ├── logging_config.py
│   │   └── error_handling.py
│   └── data/                  # Data processing modules
│       └── __init__.py
│
├── data-pipeline/             # Data processing pipeline
│   ├── configs/               # Pipeline configurations
│   │   └── pipeline_config.json
│   ├── data/                   # Data storage
│   │   ├── raw/               # Raw data (DVC tracked)
│   │   └── processed/         # Processed data
│   ├── scripts/               # Pipeline scripts
│   │   ├── main_pipeline.py
│   │   ├── preprocessing.py
│   │   ├── validation.py
│   │   ├── feature_engineering.py
│   │   ├── bias_detection.py
│   │   └── automated_bias_handler.py
│   ├── notebooks/             # Jupyter notebooks
│   │   └── data_acquisition.ipynb
│   ├── tests/                 # Pipeline tests
│   │   ├── __init__.py
│   │   ├── test_preprocessing.py
│   │   ├── test_validation.py
│   │   └── test_feature_engineering.py
│   ├── logs/                  # Pipeline logs and reports
│   ├── requirements.txt       # Pipeline dependencies
│   ├── dvc.yaml               # DVC pipeline configuration
│   └── README.md              # Pipeline documentation
│
├── scripts/                    # Utility scripts
│   ├── setup_gemini_api_key.py
│   ├── setup_gcp_auth.sh
│   ├── install_gcloud_macos.sh
│   ├── test_gemini_models.py
│   ├── train_gemini_simple.py
│   └── train_with_risk_prediction.py
│
├── tests/                      # Unit tests (consolidated)
│   ├── test_preprocessing.py
│   └── test_validation.py
│
├── configs/                    # Global configuration files
│   └── gemini_config.json
│
├── docs/                       # Documentation
│   ├── archive/               # Archived/old documentation
│   ├── guides/                # User guides
│   ├── MODEL_DEVELOPMENT_GUIDE.md
│   ├── MODEL_DEVELOPMENT_CHECKLIST.md
│   ├── COMPLETE_REQUIREMENTS_STATUS.md
│   ├── BIGQUERY_SETUP.md
│   ├── MEDICAL_IMAGE_ANALYSIS.md
│   ├── RISK_PREDICTION.md
│   └── ... (other docs)
│
├── models/                     # Trained models (gitignored)
│   └── gemini/
│
├── logs/                       # Application logs (gitignored)
│
├── mlruns/                     # MLflow runs (gitignored)
│
├── .env                        # Environment variables (gitignored)
│
├── Dockerfile                  # Docker containerization
├── docker-compose.yml          # Docker orchestration
├── .dockerignore              # Docker ignore rules
│
├── requirements.txt           # Main dependencies
├── .gitignore                 # Git ignore rules
│
├── LICENSE                    # Project license
├── README.md                  # Main README
├── CONTRIBUTING.md            # Contribution guidelines
├── CHANGELOG.md               # Version history
└── PROJECT_STRUCTURE.md       # This file
```

## Key Directories

### `src/`
Contains all source code modules:
- **training/**: Model training, validation, and MLOps components
- **utils/**: Shared utilities (logging, error handling)
- **data/**: Data processing modules

### `data-pipeline/`
Complete data processing pipeline:
- **scripts/**: Pipeline execution scripts
- **configs/**: Pipeline configuration
- **data/**: Data storage (raw and processed)
- **tests/**: Pipeline-specific tests
- **notebooks/**: Data exploration notebooks

### `scripts/`
Utility scripts for setup and operations:
- API key setup
- GCP authentication
- Model testing
- Training scripts

### `docs/`
All documentation:
- **guides/**: User guides
- **archive/**: Old/archived documentation
- Feature documentation
- Setup guides

### `tests/`
Consolidated unit tests (pipeline tests remain in `data-pipeline/tests/`)

## File Organization Principles

1. **Separation of Concerns**: Source code, data, configs, and docs are separated
2. **Modularity**: Each component is self-contained with its own tests
3. **Documentation**: All docs in `docs/` directory
4. **Configuration**: Configs in `configs/` or component-specific `configs/` subdirectories
5. **Tests**: Tests co-located with code or in dedicated `tests/` directories

## Standard Files

- **README.md**: Main project documentation
- **CONTRIBUTING.md**: Contribution guidelines
- **CHANGELOG.md**: Version history
- **LICENSE**: Project license
- **requirements.txt**: Python dependencies
- **.gitignore**: Git ignore rules
- **Dockerfile**: Containerization
- **docker-compose.yml**: Docker orchestration

## Ignored Files

The following are gitignored (see `.gitignore`):
- Virtual environments (`.venv/`, `venv/`)
- Python cache (`__pycache__/`)
- Data files (`*.csv`, `*.parquet`)
- Model files (`models/`)
- Logs (`logs/`)
- MLflow runs (`mlruns/`)
- Environment variables (`.env`)
- Credentials (`credentials/`)

