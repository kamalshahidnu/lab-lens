# Model Deployment

This directory contains code for deploying models to production.

## Structure

- `api/` - FastAPI application for model serving
- `web/` - Streamlit web interface
- `containerization/` - Docker configurations
- `scripts/` - Deployment automation scripts

## API Deployment

### Local Development

Run the FastAPI application locally:

```bash
cd model_deployment/api
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

The API will be available at:
- **API**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

### Cloud Run Deployment

Deploy the FastAPI backend to Google Cloud Run:

```bash
./model_deployment/scripts/deploy-api-to-cloud-run.sh <project-id>
```

Or manually:

```bash
# Build and deploy
gcloud builds submit --config=infrastructure/docker/cloudbuild-api.yaml
gcloud run deploy lab-lens-api \
  --image gcr.io/<project-id>/lab-lens-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /info` - Model information
- `POST /summarize` - Generate medical discharge summary
  - Request body: `{"text": "discharge summary text..."}`
  - Response: `{"summary": "...", "diagnosis": "...", "bart_summary": "..."}`

## Web Interface Deployment

### Local Development

Run the Streamlit web app locally:

```bash
cd model_deployment/web
streamlit run file_qa_web.py
```

### Cloud Run Deployment

Deploy the Streamlit web interface to Google Cloud Run:

```bash
./model_deployment/scripts/deploy-to-cloud-run.sh <project-id>
```

Or use the GitHub Actions workflow (automated on push to main).

## Docker

### Streamlit Web App

Build and run the Streamlit web app with Docker:

```bash
cd infrastructure/docker
docker build --build-arg SKIP_MODEL_DOWNLOAD=true -f Dockerfile.cloudrun -t lab-lens-web:latest .
docker run -p 8501:8501 lab-lens-web:latest
```

### FastAPI Backend

Build and run the FastAPI backend with Docker:

```bash
cd infrastructure/docker
docker build --build-arg SKIP_MODEL_DOWNLOAD=true -f Dockerfile.api -t lab-lens-api:latest .
docker run -p 8080:8080 -e GEMINI_API_KEY=your-key lab-lens-api:latest
```

## CI/CD

Both services have automated deployment via GitHub Actions:

- **Web App**: `.github/workflows/deploy-cloud-run.yml`
- **API Backend**: `.github/workflows/deploy-api-cloud-run.yml`

Deployments are triggered automatically on push to `main` branch when relevant files change.

