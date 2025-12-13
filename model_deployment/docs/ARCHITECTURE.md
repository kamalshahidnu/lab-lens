# 🚀 Model Deployment Architecture - Complete Guide

This document explains how Lab Lens models are deployed, covering both the **Frontend (Streamlit Web App)** and **Backend (FastAPI API)** deployments.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Frontend Deployment (Streamlit Web App)](#frontend-deployment-streamlit-web-app)
3. [Backend Deployment (FastAPI API)](#backend-deployment-fastapi-api)
4. [Deployment Infrastructure](#deployment-infrastructure)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Container Configuration](#container-configuration)

---

## Architecture Overview

Lab Lens has **two main deployment components**:

1. **Frontend**: Streamlit web application (`file_qa_web.py`)
   - User interface for document Q&A
   - Handles file uploads and chat interactions
   - Uses RAG (Retrieval-Augmented Generation) for document queries
   - Deployed as a single-container service

2. **Backend**: FastAPI REST API (`app.py`)
   - Medical discharge summary generation endpoint
   - Uses MedicalSummarizer (BART model + Gemini refinement)
   - Provides `/summarize` endpoint for backend processing
   - Can be used independently or integrated with frontend

**Deployment Platform**: Both services are deployed on **Google Cloud Run**, a serverless container platform.

---

## Frontend Deployment (Streamlit Web App)

### Overview
The frontend is a Streamlit application that provides a chat-based interface for document Q&A. It combines:
- **BioBERT embeddings** for semantic search
- **Gemini API** for answer generation
- **Medical summarization** capabilities

### Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│         GitHub Repository (main branch)         │
└─────────────────┬───────────────────────────────┘
                  │
                  │ Push to main branch
                  │ (triggers on file changes)
                  ▼
┌─────────────────────────────────────────────────┐
│      GitHub Actions CI/CD Workflow              │
│   (.github/workflows/deploy-cloud-run.yml)      │
└─────────────────┬───────────────────────────────┘
                  │
                  │ 1. Checkout code
                  │ 2. Authenticate to GCP
                  │ 3. Build Docker image
                  │ 4. Push to Google Container Registry
                  │ 5. Deploy to Cloud Run
                  ▼
┌─────────────────────────────────────────────────┐
│     Google Cloud Build (Docker Build)           │
│     Image: gcr.io/PROJECT_ID/lab-lens-web       │
└─────────────────┬───────────────────────────────┘
                  │
                  │ Dockerfile.cloudrun
                  │ - Python 3.12-slim base
                  │ - Pre-installs ML models
                  │ - Configures Streamlit
                  ▼
┌─────────────────────────────────────────────────┐
│       Google Cloud Run Service                  │
│       Service: lab-lens-web                     │
│       Region: us-central1                       │
│       Port: 8501                                │
│       Memory: 4Gi, CPU: 2                       │
│       Min instances: 0, Max: 10                 │
└─────────────────────────────────────────────────┘
                  │
                  │ Public URL (HTTPS)
                  ▼
            End Users / Web Browser
```

### Deployment Steps

#### 1. **Trigger Conditions**
The deployment is automatically triggered when code is pushed to the `main` branch and files in these paths change:
- `model_deployment/**`
- `infrastructure/**`
- `src/**`
- `requirements.txt`
- `.github/workflows/deploy-cloud-run.yml`

#### 2. **GitHub Actions Workflow** (`.github/workflows/deploy-cloud-run.yml`)

**Steps:**
1. **Checkout code** - Gets the latest code from repository
2. **Verify secrets** - Ensures GCP credentials are configured
3. **Authenticate to GCP** - Uses service account key from GitHub secrets
4. **Set up Cloud SDK** - Configures `gcloud` CLI
5. **Build and push container** - Builds Docker image using `infrastructure/docker/Dockerfile.cloudrun`
6. **Deploy to Cloud Run** - Deploys the service with configuration:
   - **Port**: 8501 (Streamlit default)
   - **Memory**: 4Gi (for ML models)
   - **CPU**: 2 cores
   - **Timeout**: 600 seconds (10 minutes)
   - **Scaling**: 0-10 instances (serverless auto-scaling)
   - **Environment variables**: Hugging Face cache paths
   - **Secrets**: Gemini API key from Secret Manager

#### 3. **Docker Container Build** (`infrastructure/docker/Dockerfile.cloudrun`)

**Key Features:**
- **Base image**: `python:3.12-slim`
- **System dependencies**: Build tools, curl, git
- **Python dependencies**: Installed from `requirements.txt` + `pdfplumber`
- **Model pre-downloading**: 
  - Downloads `all-MiniLM-L6-v2` embedding model during build
  - Downloads `dmis-lab/biobert-base-cased-v1.2` (BioBERT) model
  - Caches models in `/root/.cache/huggingface` to avoid cold starts
- **Health check**: Monitors `/_stcore/health` endpoint
- **Entry point**: Runs `streamlit run model_deployment/web/file_qa_web.py`

**Model Pre-loading Strategy:**
```dockerfile
# Pre-download embedding models during build
RUN python3 -c "from sentence_transformers import SentenceTransformer; \
    model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/root/.cache/huggingface')"
```
This ensures models are available immediately when the container starts, reducing cold start time.

#### 4. **Cloud Run Configuration**

**Resource Allocation:**
- **Memory**: 4Gi (required for ML models like BioBERT and MedicalSummarizer)
- **CPU**: 2 cores (for faster inference)
- **Timeout**: 600 seconds (for long-running queries)
- **Concurrency**: Default (Cloud Run managed)

**Scaling:**
- **Min instances**: 0 (scales to zero when not in use - cost-effective)
- **Max instances**: 10 (limits concurrent requests)
- **Auto-scaling**: Automatically scales based on traffic

**Environment & Secrets:**
- **Environment variables**: 
  - `HF_HOME=/root/.cache/huggingface`
  - `TRANSFORMERS_CACHE=/root/.cache/huggingface`
- **Secrets** (from Google Secret Manager):
  - `GEMINI_API_KEY=gemini-api-key:latest`
  - `GOOGLE_API_KEY=gemini-api-key:latest`

**Networking:**
- **Allow unauthenticated**: Yes (public access)
- **HTTPS**: Automatically provided by Cloud Run
- **Custom domain**: Can be configured if needed

#### 5. **Health Checks & Monitoring**

- **Health endpoint**: `/_stcore/health` (Streamlit built-in)
- **Health check**: Runs every 30 seconds
- **Startup period**: 40 seconds (allows model loading)
- **Retries**: 3 attempts before marking unhealthy

#### 6. **Deployment Verification**

After deployment, the workflow:
1. Gets the service URL from Cloud Run
2. Waits 15 seconds for service to be ready
3. Tests the health endpoint
4. Comments on PR if deployed from a pull request

---

## Backend Deployment (FastAPI API)

### Overview
The backend is a FastAPI REST API that provides medical discharge summary generation. It's designed to be used:
- As a standalone API service
- Integrated with other applications
- Called from the frontend when needed

### Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│         GitHub Repository (main branch)         │
└─────────────────┬───────────────────────────────┘
                  │
                  │ Push to main branch
                  │ (API-related file changes)
                  ▼
┌─────────────────────────────────────────────────┐
│   GitHub Actions CI/CD Workflow                 │
│   (.github/workflows/deploy-api-cloud-run.yml)  │
└─────────────────┬───────────────────────────────┘
                  │
                  │ Similar workflow to frontend
                  ▼
┌─────────────────────────────────────────────────┐
│     Google Cloud Build (Docker Build)           │
│     Image: gcr.io/PROJECT_ID/lab-lens-api       │
└─────────────────┬───────────────────────────────┘
                  │
                  │ Dockerfile.api
                  │ - Python 3.12-slim base
                  │ - FastAPI + Uvicorn
                  │ - Pre-loads MedicalSummarizer
                  ▼
┌─────────────────────────────────────────────────┐
│       Google Cloud Run Service                  │
│       Service: lab-lens-api                     │
│       Region: us-central1                       │
│       Port: 8080                                │
│       Memory: 4Gi, CPU: 2                       │
└─────────────────────────────────────────────────┘
                  │
                  │ REST API (HTTPS)
                  ▼
            API Clients / Frontend
```

### Key Differences from Frontend

1. **Port**: 8080 (standard for APIs)
2. **Framework**: FastAPI instead of Streamlit
3. **Entry point**: `uvicorn model_deployment.api.app:app`
4. **Endpoints**:
   - `GET /` - API information
   - `GET /health` - Health check
   - `GET /info` - Model information
   - `POST /summarize` - Generate medical summary

### API Endpoints

#### POST /summarize
**Request:**
```json
{
  "text": "discharge summary text here..."
}
```

**Response:**
```json
{
  "summary": "Patient-friendly summary...",
  "diagnosis": "Primary diagnoses...",
  "bart_summary": "BART model summary..."
}
```

#### Model Loading
The MedicalSummarizer model is loaded at startup:
```python
@app.on_event("startup")
async def load_model():
    global summarizer
    summarizer = MedicalSummarizer(use_gpu=False)
```

This ensures the model is ready before handling requests.

---

## Deployment Infrastructure

### 1. Docker Images

Both services use similar Docker base images but different configurations:

| Component | Dockerfile | Base Image | Key Features |
|-----------|-----------|------------|--------------|
| Frontend | `Dockerfile.cloudrun` | python:3.12-slim | Streamlit, pre-downloaded embeddings |
| Backend | `Dockerfile.api` | python:3.12-slim | FastAPI, Uvicorn, pre-loaded models |

### 2. Google Container Registry (GCR)

All Docker images are stored in Google Container Registry:
- **Frontend**: `gcr.io/PROJECT_ID/lab-lens-web`
- **Backend**: `gcr.io/PROJECT_ID/lab-lens-api`

Images are automatically built and pushed during CI/CD pipeline.

### 3. Cloud Run Services

Both services run as separate Cloud Run services:

| Service | URL Pattern | Purpose |
|---------|------------|---------|
| lab-lens-web | `https://lab-lens-web-*.run.app` | User-facing web interface |
| lab-lens-api | `https://lab-lens-api-*.run.app` | API for summary generation |

### 4. Secret Management

**Google Secret Manager** is used for sensitive data:
- Secret name: `gemini-api-key`
- Version: `latest`
- Accessed by: Both services via Cloud Run secrets

**Setup:**
```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-

# Grant Cloud Run access
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## CI/CD Pipeline

### Automated Deployment Triggers

#### Frontend (Streamlit)
**Workflow**: `.github/workflows/deploy-cloud-run.yml`

**Triggers:**
- Push to `main` branch when files in these paths change:
  - `model_deployment/**`
  - `infrastructure/**`
  - `src/**`
  - `requirements.txt`
- Manual trigger via `workflow_dispatch` (with environment selection)

**Steps:**
1. ✅ Verify GitHub secrets are set
2. 🔐 Authenticate to GCP using service account key
3. 🏗️ Build Docker image using Cloud Build
4. 📦 Push image to Google Container Registry
5. 🚀 Deploy to Cloud Run
6. ✅ Verify deployment with health check
7. 💬 Comment on PR with deployment URL

#### Backend (FastAPI)
**Workflow**: `.github/workflows/deploy-api-cloud-run.yml`

Similar process but for the API service.

### GitHub Secrets Required

```yaml
GCP_PROJECT_ID: "your-gcp-project-id"
GCP_SA_KEY: "service-account-key-json"
```

### Manual Deployment

You can also deploy manually:

**Frontend:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/lab-lens-web \
  --file infrastructure/docker/Dockerfile.cloudrun

gcloud run deploy lab-lens-web \
  --image gcr.io/PROJECT_ID/lab-lens-web \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 4Gi \
  --cpu 2
```

**Backend:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/lab-lens-api \
  --file infrastructure/docker/Dockerfile.api

gcloud run deploy lab-lens-api \
  --image gcr.io/PROJECT_ID/lab-lens-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 4Gi \
  --cpu 2
```

---

## Container Configuration

### Shared Configuration

Both containers share:
- **Python version**: 3.12
- **Base image**: `python:3.12-slim`
- **System packages**: build-essential, curl, git
- **Model caching**: `/root/.cache/huggingface`
- **Environment variables**:
  - `HF_HOME=/root/.cache/huggingface`
  - `TRANSFORMERS_CACHE=/root/.cache/huggingface`
  - `PYTHONPATH=/app`

### Frontend-Specific

**Dockerfile.cloudrun:**
- Pre-downloads embedding models (all-MiniLM-L6-v2, BioBERT)
- Installs `pdfplumber` for PDF processing
- Sets Streamlit environment variables
- Runs Streamlit on port 8501
- Health check: `/_stcore/health`

**Entry point:**
```dockerfile
CMD streamlit run model_deployment/web/file_qa_web.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true
```

### Backend-Specific

**Dockerfile.api:**
- Pre-downloads embedding models (same as frontend)
- Runs FastAPI with Uvicorn
- Health check: `/health`

**Entry point:**
```dockerfile
CMD exec uvicorn model_deployment.api.app:app \
    --host 0.0.0.0 \
    --port ${PORT:-8080} \
    --workers 1
```

### Model Optimization Strategies

1. **Pre-downloading during build**: Models are downloaded during Docker build, not at runtime
2. **Caching**: Models are cached in `/root/.cache/huggingface` which persists across container restarts
3. **Lazy loading**: Models are loaded on first use in the application code
4. **Memory allocation**: 4Gi memory ensures models fit in RAM

---

## Cost Optimization

### Cloud Run Pricing Model

Cloud Run charges for:
- **CPU and memory**: Only when handling requests
- **Requests**: Per million requests
- **Min instances = 0**: No charges when not in use (recommended for development)
- **Min instances = 1**: Prevents cold starts but incurs minimal cost even when idle

### Recommended Settings

**Development/Testing:**
- Min instances: 0
- Max instances: 5
- Memory: 2Gi (if models fit)

**Production:**
- Min instances: 1 (eliminates cold starts)
- Max instances: 10-20 (based on traffic)
- Memory: 4Gi (for full model support)

---

## Monitoring & Troubleshooting

### View Logs

```bash
# Frontend logs
gcloud run services logs tail lab-lens-web --region us-central1

# Backend logs
gcloud run services logs tail lab-lens-api --region us-central1
```

### Common Issues

1. **Cold starts slow**: 
   - Solution: Set `--min-instances 1`
   - Models are pre-downloaded but still need to load into memory

2. **Out of memory errors**:
   - Solution: Increase to 4Gi memory
   - Check model sizes: BioBERT ~400MB, MedicalSummarizer ~500MB

3. **Timeout errors**:
   - Solution: Increase timeout to 600 seconds
   - First request may take 30-60 seconds (model loading)

4. **Health check failures**:
   - Verify health endpoint is accessible
   - Check application logs for startup errors

---

## Summary

### Frontend Deployment Flow
```
Code Push → GitHub Actions → Build Docker Image → Push to GCR → Deploy to Cloud Run → Public URL
```

### Backend Deployment Flow
```
Code Push → GitHub Actions → Build Docker Image → Push to GCR → Deploy to Cloud Run → API URL
```

### Key Technologies
- **Containerization**: Docker
- **Container Registry**: Google Container Registry (GCR)
- **Orchestration**: Google Cloud Run (serverless)
- **CI/CD**: GitHub Actions
- **Secrets**: Google Secret Manager
- **Frontend**: Streamlit
- **Backend**: FastAPI + Uvicorn

Both services are deployed independently but can work together. The frontend provides the user interface, while the backend can be used for programmatic access to the summarization models.


