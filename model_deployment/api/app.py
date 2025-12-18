import json
import logging
import os
import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from monitoring.model_monitoring import InferenceMonitor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to hold the model
summarizer = None
summarizer_init_lock = threading.Lock()
monitor = InferenceMonitor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.

    IMPORTANT: On Cloud Run, loading large ML models during startup can cause
    deploy-time failures (cold start timeouts / readiness failures). We therefore
    keep startup lightweight and load the summarizer lazily on first request.

    If you *do* want to warm the model at startup (at the cost of longer cold
    starts), set PRELOAD_SUMMARIZER=true.
    """
    global summarizer
    if str(os.getenv("PRELOAD_SUMMARIZER", "")).lower() in ("1", "true", "yes", "y"):
        try:
            logger.info("Preloading Medical Summarizer (PRELOAD_SUMMARIZER=true)...")
            from model_deployment.api.summarizer import MedicalSummarizer

            summarizer = MedicalSummarizer(use_gpu=False)
            logger.info(" Summarizer preloaded successfully!")
        except Exception as e:
            logger.error(f" Summarizer preload failed; will retry lazily: {e}")
            summarizer = None
    else:
        logger.info("Skipping summarizer preload (lazy-load enabled).")

    yield  # Application runs here

    # Shutdown logic (if needed)
    logger.info("Shutting down API...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Medical Discharge Summarizer API",
    description="AI-powered medical discharge summary generation",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request and Response models
class DischargeRequest(BaseModel):
    text: str


class SummaryResponse(BaseModel):
    summary: str
    diagnosis: str
    bart_summary: str


def get_or_init_summarizer():
    """Thread-safe lazy initialization of the summarizer."""
    global summarizer
    if summarizer is not None:
        return summarizer

    with summarizer_init_lock:
        if summarizer is not None:
            return summarizer
        logger.info("Lazy-loading Medical Summarizer...")
        # Import here to avoid importing torch/transformers during container startup.
        from model_deployment.api.summarizer import MedicalSummarizer

        summarizer = MedicalSummarizer(use_gpu=False)
        logger.info(" Summarizer loaded successfully (lazy).")
        return summarizer


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Medical Discharge Summarizer API",
        "status": "running",
        "endpoints": {"health": "/health", "summarize": "/summarize", "docs": "/docs"},
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        # Always return 200 so the container can become ready on Cloud Run.
        "status": "healthy" if summarizer is not None else "starting",
        "model_loaded": summarizer is not None,
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.post("/summarize", response_model=SummaryResponse)
def summarize(request: DischargeRequest):
    """Generate patient-friendly summary from discharge text"""
    if not request.text or len(request.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Text too short (minimum 50 characters)")

    start = time.time()
    try:
        logger.info(f"Processing summary request (text length: {len(request.text)} chars)")
        summarizer_instance = get_or_init_summarizer()

        # Generate summary
        result = summarizer_instance.generate_summary(request.text)

        # Debug: Print what keys are in result
        logger.info(f"Result keys: {list(result.keys())}")

        # Extract values with safe fallbacks
        summary = result.get("final_summary", "")
        diagnosis = result.get("extracted_data", {}).get("diagnosis", "Unknown")
        bart_summary = result.get("summary", "")  # Changed from 'bart_summary' to 'summary'

        latency_ms = int((time.time() - start) * 1000)
        event = monitor.record(
            input_text=request.text,
            output_text=summary,
            latency_ms=latency_ms,
            success=True,
            error_type=None,
        )
        if event.get("enabled"):
            logger.info("MODEL_MONITOR " + json.dumps(event, ensure_ascii=False))

        return SummaryResponse(summary=summary, diagnosis=diagnosis, bart_summary=bart_summary)

    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        latency_ms = int((time.time() - start) * 1000)
        event = monitor.record(
            input_text=request.text,
            output_text="",
            latency_ms=latency_ms,
            success=False,
            error_type=type(e).__name__,
        )
        if event.get("enabled"):
            logger.info("MODEL_MONITOR " + json.dumps(event, ensure_ascii=False))
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@app.get("/monitoring/status")
def monitoring_status():
    """
    Model monitoring status: rolling stats + drift flags for the summarizer.
    Intended for debugging/validation (no sensitive payloads).
    """
    return monitor.status()


@app.get("/info")
def info():
    """Get API information"""
    return {
        "model_id": os.getenv("MODEL_ID", "asadwaraich/bart-medical-discharge-summarizer"),
        "device": "cpu",
        "gemini_enabled": bool(os.getenv("GEMINI_API_KEY")),
        "version": "1.0.0",
    }
