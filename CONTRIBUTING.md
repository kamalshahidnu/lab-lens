# Contributing to Lab Lens

Thank you for your interest in contributing to Lab Lens! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/lab-lens.git
cd lab-lens
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate # Mac/Linux
# or
.venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r data_pipeline/requirements.txt

# Install development dependencies
pip install black isort flake8 mypy pytest pytest-cov
```

### 3. Set Up Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clear, readable code
- Follow the existing code style
- Add docstrings to functions and classes
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov=data_pipeline

# Run specific test file
pytest tests/test_validation.py
```

### 4. Code Formatting

```bash
# Format code with black
black src/ data_pipeline/scripts/ scripts/

# Sort imports
isort src/ data_pipeline/scripts/ scripts/

# Check linting
flake8 src/ data_pipeline/scripts/ scripts/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
# or
git commit -m "fix: fix bug description"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guide
- Use type hints where possible
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md if adding new features

### Testing

- Write tests for new features
- Aim for >80% code coverage
- Test edge cases and error conditions

## Project Structure

```
lab-lens/
├── src/          # Source code
│  ├── training/     # Model training modules
│  ├── utils/       # Utility modules
│  └── data/       # Data processing modules
├── data_pipeline/ # Data processing pipeline (single source of truth)
│  ├── scripts/      # Pipeline scripts
│  ├── configs/      # Configuration files
│  └── tests/       # Pipeline tests
├── scripts/        # Utility scripts
├── tests/         # Unit tests
├── docs/         # Documentation
├── configs/        # Global configurations
└── .github/        # GitHub workflows
```

## Pull Request Process

1. **Update Documentation**: Update README.md and relevant docs
2. **Add Tests**: Ensure new code is tested
3. **Update CHANGELOG.md**: Document your changes
4. **Ensure CI Passes**: All tests and checks must pass
5. **Request Review**: Request review from maintainers

## Reporting Issues

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages/logs

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternatives considered

## Questions?

- Open an issue for questions
- Check existing documentation in `docs/`
- Review existing code for examples

Thank you for contributing to Lab Lens! 🎉




