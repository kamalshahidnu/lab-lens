"""
Model monitoring utilities for Lab Lens.

Goal: lightweight, dependency-minimal model monitoring that works on Cloud Run.

What we track (per inference):
- input text length (chars / words)
- output length (chars)
- latency (ms)
- success / error type
- model identifiers (MODEL_ID, image tag if provided)

We maintain rolling online statistics and compare to an optional baseline to flag drift.
Baseline is intentionally simple (mean/std + thresholds) so it can be configured via env.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


def _now_ms() -> int:
  return int(time.time() * 1000)


def _safe_int(x: Any, default: int = 0) -> int:
  try:
    return int(x)
  except Exception:
    return default


@dataclass
class DriftThresholds:
  """
  Drift rule: flag when |current_mean - baseline_mean| > z * baseline_std.
  """

  z_input_chars: float = 3.0
  z_input_words: float = 3.0
  z_output_chars: float = 3.0
  max_error_rate: float = 0.15
  max_p95_latency_ms: int = 30_000

  @staticmethod
  def from_env() -> "DriftThresholds":
    def f(name: str, default: float) -> float:
      try:
        return float(os.getenv(name, str(default)))
      except Exception:
        return default

    return DriftThresholds(
      z_input_chars=f("MONITOR_Z_INPUT_CHARS", 3.0),
      z_input_words=f("MONITOR_Z_INPUT_WORDS", 3.0),
      z_output_chars=f("MONITOR_Z_OUTPUT_CHARS", 3.0),
      max_error_rate=f("MONITOR_MAX_ERROR_RATE", 0.15),
      max_p95_latency_ms=_safe_int(os.getenv("MONITOR_MAX_P95_LATENCY_MS", "30000"), 30000),
    )


class OnlineStats:
  """Welford online mean/variance."""

  def __init__(self) -> None:
    self.n = 0
    self.mean = 0.0
    self.m2 = 0.0

  def update(self, x: float) -> None:
    self.n += 1
    delta = x - self.mean
    self.mean += delta / self.n
    delta2 = x - self.mean
    self.m2 += delta * delta2

  @property
  def variance(self) -> float:
    return (self.m2 / (self.n - 1)) if self.n > 1 else 0.0

  @property
  def std(self) -> float:
    v = self.variance
    return v ** 0.5

  def to_dict(self) -> Dict[str, Any]:
    return {"n": self.n, "mean": self.mean, "std": self.std}


class LatencyReservoir:
  """
  Keep a bounded sample of latencies to approximate p95 without heavy deps.
  """

  def __init__(self, maxlen: int = 512) -> None:
    self.maxlen = maxlen
    self._vals = [] # type: ignore[var-annotated]

  def add(self, ms: int) -> None:
    self._vals.append(ms)
    if len(self._vals) > self.maxlen:
      # drop oldest half to keep some history
      self._vals = self._vals[len(self._vals) // 2 :]

  def p95(self) -> int:
    if not self._vals:
      return 0
    vals = sorted(self._vals)
    idx = max(0, int(0.95 * (len(vals) - 1)))
    return int(vals[idx])

  def to_dict(self) -> Dict[str, Any]:
    return {"sample_size": len(self._vals), "p95_ms": self.p95()}


class InferenceMonitor:
  """
  Thread-safe in-process monitor.

  This does NOT attempt durable storage on Cloud Run filesystem. Instead:
  - emits structured JSON logs (Cloud Logging is the durable store)
  - exposes current rolling stats via /monitoring/status
  """

  def __init__(self) -> None:
    self.enabled = str(os.getenv("MODEL_MONITORING_ENABLED", "true")).lower() not in ("0", "false", "no")
    self.thresholds = DriftThresholds.from_env()
    self._lock = threading.Lock()

    self.input_chars = OnlineStats()
    self.input_words = OnlineStats()
    self.output_chars = OnlineStats()
    self.latency = LatencyReservoir()

    self.total = 0
    self.errors = 0

    # Optional baseline (set via env) — defaults to "no baseline" (drift checks disabled).
    self.baseline = self._load_baseline_from_env()

  def _load_baseline_from_env(self) -> Optional[Dict[str, Any]]:
    raw = os.getenv("MODEL_MONITOR_BASELINE_JSON", "").strip()
    if not raw:
      return None
    try:
      return json.loads(raw)
    except Exception:
      return None

  def record(
    self,
    *,
    input_text: str,
    output_text: str,
    latency_ms: int,
    success: bool,
    error_type: Optional[str] = None,
  ) -> Dict[str, Any]:
    if not self.enabled:
      return {"enabled": False}

    in_chars = len(input_text or "")
    in_words = len((input_text or "").split())
    out_chars = len(output_text or "")

    with self._lock:
      self.total += 1
      if not success:
        self.errors += 1

      self.input_chars.update(float(in_chars))
      self.input_words.update(float(in_words))
      self.output_chars.update(float(out_chars))
      self.latency.add(int(latency_ms))

      drift = self._check_drift_locked()

      return {
        "enabled": True,
        "ts_ms": _now_ms(),
        "model_id": os.getenv("MODEL_ID", "unknown"),
        "model_image": os.getenv("K_REVISION", ""), # Cloud Run revision if available
        "input_chars": in_chars,
        "input_words": in_words,
        "output_chars": out_chars,
        "latency_ms": int(latency_ms),
        "success": bool(success),
        "error_type": error_type,
        "drift": drift,
      }

  def _z_score(self, current_mean: float, baseline_mean: float, baseline_std: float) -> float:
    if baseline_std <= 1e-9:
      return 0.0
    return abs(current_mean - baseline_mean) / baseline_std

  def _check_drift_locked(self) -> Dict[str, Any]:
    # If no baseline, only check "hard" SLO-ish rules.
    error_rate = (self.errors / self.total) if self.total else 0.0
    p95 = self.latency.p95()

    out: Dict[str, Any] = {
      "has_baseline": bool(self.baseline),
      "error_rate": error_rate,
      "p95_latency_ms": p95,
      "alerts": [],
    }

    if error_rate > self.thresholds.max_error_rate:
      out["alerts"].append({"type": "high_error_rate", "value": error_rate, "threshold": self.thresholds.max_error_rate})
    if p95 > self.thresholds.max_p95_latency_ms:
      out["alerts"].append({"type": "high_p95_latency", "value": p95, "threshold": self.thresholds.max_p95_latency_ms})

    if not self.baseline:
      return out

    b = self.baseline
    try:
      # expected format: {"input_chars": {"mean":..,"std":..}, ...}
      z_in_chars = self._z_score(self.input_chars.mean, float(b["input_chars"]["mean"]), float(b["input_chars"]["std"]))
      z_in_words = self._z_score(self.input_words.mean, float(b["input_words"]["mean"]), float(b["input_words"]["std"]))
      z_out_chars = self._z_score(self.output_chars.mean, float(b["output_chars"]["mean"]), float(b["output_chars"]["std"]))
    except Exception:
      return out

    out["z"] = {
      "input_chars": z_in_chars,
      "input_words": z_in_words,
      "output_chars": z_out_chars,
    }

    if z_in_chars > self.thresholds.z_input_chars:
      out["alerts"].append({"type": "drift_input_chars", "z": z_in_chars, "threshold": self.thresholds.z_input_chars})
    if z_in_words > self.thresholds.z_input_words:
      out["alerts"].append({"type": "drift_input_words", "z": z_in_words, "threshold": self.thresholds.z_input_words})
    if z_out_chars > self.thresholds.z_output_chars:
      out["alerts"].append({"type": "drift_output_chars", "z": z_out_chars, "threshold": self.thresholds.z_output_chars})

    return out

  def status(self) -> Dict[str, Any]:
    if not self.enabled:
      return {"enabled": False}
    with self._lock:
      return {
        "enabled": True,
        "model_id": os.getenv("MODEL_ID", "unknown"),
        "model_image": os.getenv("K_REVISION", ""),
        "counts": {"total": self.total, "errors": self.errors, "error_rate": (self.errors / self.total) if self.total else 0.0},
        "stats": {
          "input_chars": self.input_chars.to_dict(),
          "input_words": self.input_words.to_dict(),
          "output_chars": self.output_chars.to_dict(),
          "latency": self.latency.to_dict(),
        },
        "thresholds": {
          "z_input_chars": self.thresholds.z_input_chars,
          "z_input_words": self.thresholds.z_input_words,
          "z_output_chars": self.thresholds.z_output_chars,
          "max_error_rate": self.thresholds.max_error_rate,
          "max_p95_latency_ms": self.thresholds.max_p95_latency_ms,
        },
        "drift": self._check_drift_locked(),
      }




