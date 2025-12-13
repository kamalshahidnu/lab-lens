"""
Lightweight metrics helpers.

This file is intentionally dependency-minimal so it works in Cloud Run and local dev
without requiring native/system packages.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict


def collect_metrics() -> Dict[str, Any]:
    """
    Collect basic runtime metadata (not ML performance metrics).

    For ML lifecycle monitoring, see `monitoring/model_monitoring.py`.
    """
    return {
        "ts_ms": int(time.time() * 1000),
        "service": os.getenv("K_SERVICE", ""),
        "revision": os.getenv("K_REVISION", ""),
        "configuration": os.getenv("K_CONFIGURATION", ""),
        "model_id": os.getenv("MODEL_ID", ""),
    }


