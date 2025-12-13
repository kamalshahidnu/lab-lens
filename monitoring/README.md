# Monitoring and Observability

This directory contains monitoring, logging, and observability code for Lab Lens.

## Structure

- `metrics.py` - Metrics collection utilities
- `logging/` - Logging configurations
- `dashboards/` - Monitoring dashboard configurations

## Usage

Collect metrics:

```python
from monitoring.metrics import collect_metrics

metrics = collect_metrics()
```

## Logging

Configure logging:

```python
from src.utils.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Application started")
```

## Cloud Monitoring

Metrics are automatically sent to Google Cloud Monitoring when deployed to Cloud Run.

## Model Monitoring (ML Lifecycle)

The API backend emits **model inference monitoring events** (structured JSON logs) and
maintains **rolling drift/quality stats** in-process.

### What is tracked

- Input size: chars/words
- Output size: chars
- Latency (ms) + p95 latency (approx)
- Error rate
- Model identifiers: `MODEL_ID` and Cloud Run `K_REVISION`

### Where to view it

- **Cloud Logging**: filter for entries containing `MODEL_MONITOR`
- **API endpoint**: `GET /monitoring/status` (no payloads; just aggregates + drift flags)

### Drift thresholds (optional)

You can configure thresholds via env vars (Cloud Run):

- `MODEL_MONITORING_ENABLED` (default `true`)
- `MONITOR_Z_INPUT_CHARS`, `MONITOR_Z_INPUT_WORDS`, `MONITOR_Z_OUTPUT_CHARS` (default `3.0`)
- `MONITOR_MAX_ERROR_RATE` (default `0.15`)
- `MONITOR_MAX_P95_LATENCY_MS` (default `30000`)

Optional baseline (advanced):

- `MODEL_MONITOR_BASELINE_JSON`: JSON string like:

  `{ "input_chars": {"mean": 1200, "std": 400}, "input_words": {"mean": 200, "std": 60}, "output_chars": {"mean": 900, "std": 300} }`

