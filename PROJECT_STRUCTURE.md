# Lab Lens - Project Structure

## Overview

This repository follows standard MLOps best practices with a clear separation of concerns across different stages of the machine learning lifecycle.

## Directory Structure

```
lab-lens/
├── README.md           # Main project documentation
├── LICENSE            # Project license
├── requirements.txt        # Main Python dependencies
├── .gitignore           # Git ignore rules
│
├── data/             # Data storage (gitignored)
│  ├── raw/            # Raw data from sources
│  ├── processed/         # Processed/cleaned data
│  ├── external/         # External datasets
│  └── .gitkeep
│
├── data_pipeline/     # Data pipeline (single source of truth)
│  ├── README.md         # Pipeline documentation
│  ├── configs/          # Pipeline configuration
│  │  └── pipeline_config.json
│  ├── scripts/          # Pipeline scripts (preprocess → validate → features → bias)
│  ├── notebooks/         # Data acquisition notebook
│  └── tests/           # Pipeline unit tests
│
├── model_development/       # Model training and development
│  ├── __init__.py
│  ├── README.md         # Model development docs
│  ├── configs/          # Training configurations
│  ├── scripts/          # Training scripts
│  │  ├── __init__.py
│  │  ├── train_gemini.py    # Gemini model training
│  │  ├── train_with_tracking.py # Training with MLflow
│  │  ├── hyperparameter_tuning.py # Hyperparameter optimization
│  │  ├── model_validation.py  # Model validation
│  │  ├── model_registry.py   # Model registry integration
│  │  └── ...
│  ├── notebooks/         # Training notebooks
│  └── experiments/        # Experiment results
│
├── model_deployment/       # Model deployment
│  ├── __init__.py
│  ├── README.md         # Deployment documentation
│  ├── api/            # API deployment (FastAPI)
│  │  ├── __init__.py
│  │  ├── app.py        # FastAPI application
│  │  └── summarizer.py     # Summarization model
│  ├── web/            # Web interface (Streamlit)
│  │  ├── __init__.py
│  │  └── file_qa_web.py    # Streamlit web app
│  ├── containerization/     # Container configs
│  │  └── ...
│  └── scripts/          # Deployment scripts
│    └── deploy-to-cloud-run.sh
│
├── monitoring/          # Monitoring and observability
│  ├── __init__.py
│  ├── README.md         # Monitoring documentation
│  ├── metrics.py         # Metrics collection
│  ├── logging/          # Logging configurations
│  └── dashboards/        # Monitoring dashboards
│
├── infrastructure/        # Infrastructure as code
│  ├── README.md         # Infrastructure docs
│  ├── docker/          # Docker configurations
│  │  ├── Dockerfile
│  │  ├── Dockerfile.cloudrun
│  │  ├── docker-compose.yml
│  │  └── cloudbuild.yaml
│  ├── kubernetes/        # Kubernetes manifests (if needed)
│  ├── terraform/         # Terraform configs (if needed)
│  └── ci_cd/           # CI/CD workflows
│    └── .github/
│      └── workflows/
│
├── src/              # Source code library
│  ├── __init__.py
│  ├── data/           # Data utilities
│  │  └── __init__.py
│  ├── rag/            # RAG system
│  │  ├── __init__.py
│  │  ├── rag_system.py     # Core RAG implementation
│  │  ├── file_qa.py      # File Q&A system
│  │  ├── patient_qa.py     # Patient Q&A interface
│  │  ├── document_processor.py # Document processing
│  │  └── vector_db.py     # Vector database
│  └── utils/           # Shared utilities
│    ├── __init__.py
│    ├── logging_config.py   # Logging configuration
│    ├── error_handling.py   # Error handling
│    └── medical_utils.py   # Medical utilities
│
├── notebooks/           # Jupyter notebooks
│  ├── exploration/        # Data exploration
│  ├── experiments/        # Experiment notebooks
│  └── .gitkeep
│
├── tests/             # Test suite
│  ├── __init__.py
│  ├── unit/           # Unit tests
│  │  └── __init__.py
│  ├── integration/       # Integration tests
│  │  └── __init__.py
│  └── e2e/            # End-to-end tests
│    └── __init__.py
│
├── configs/            # Global configurations
│  └── ...
│
├── scripts/            # Utility scripts
│  ├── setup.sh
│  ├── setup_gcp_auth.sh
│  └── ...
│
└── docs/             # Documentation
  ├── README.md
  ├── deployment/        # Deployment guides
  ├── api/            # API documentation
  └── ...
```

## Key Principles

1. **Separation of Concerns**: Each directory has a clear, single responsibility
2. **Modularity**: Code is organized into reusable modules
3. **Testability**: Tests are organized by type (unit, integration, e2e)
4. **Documentation**: Each major component has its own README
5. **Infrastructure as Code**: All infrastructure configs are version controlled

## Workflow

1. **Data Pipeline**: `data_pipeline/` - Preprocess, validate, engineer features, detect/mitigate bias
2. **Model Development**: `model_development/` - Train and validate models
3. **Model Deployment**: `model_deployment/` - Deploy models to production
4. **Monitoring**: `monitoring/` - Monitor deployed models
5. **Infrastructure**: `infrastructure/` - Manage deployment infrastructure

## Import Paths

After restructuring, update imports to use the new structure:

```python
# The Swetha data pipeline scripts are plain Python modules under
# `data_pipeline/scripts/` (not a Python package). Import them by
# adding that folder to your Python path:
import sys

sys.path.insert(0, "data_pipeline/scripts")
from preprocessing import MIMICPreprocessor
```
