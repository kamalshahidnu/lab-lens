# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Medical image analysis module for chest X-rays, CT scans, and MRIs
- Risk prediction functionality based on medical conditions
- Model rollback mechanism for automatic performance-based rollback
- Docker containerization with multi-stage builds
- Docker Compose for full pipeline orchestration
- Enhanced model selection after bias checking
- Complete CI/CD pipeline with rollback checking
- Comprehensive documentation for all features

### Changed
- Enhanced model selection to consider both validation metrics and bias scores
- Improved CI/CD pipeline with rollback integration
- Updated project structure for better organization

### Fixed
- Type conversion issues in risk prediction module
- Import errors in training modules
- NumPy compatibility warnings

## [1.0.0] - 2024-11-18

### Added
- Initial release of Lab Lens
- Gemini 2.5 Flash integration for medical text summarization
- MIMIC-III data processing pipeline
- Bias detection and mitigation
- Model validation with ROUGE/BLEU metrics
- Hyperparameter tuning with Optuna
- MLflow experiment tracking
- Model registry integration
- Sensitivity analysis with SHAP/LIME
- BigQuery integration for MIMIC-III data access

### Features
- Medical report summarization
- Automated bias detection
- Data quality validation
- Complete MLOps pipeline




