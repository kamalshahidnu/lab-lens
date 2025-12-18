import os

import pytest
import requests


def _get_base_url() -> str | None:
    # Prefer explicit config; fall back to deploy workflow output name.
    return os.getenv("LAB_LENS_API_URL") or os.getenv("SERVICE_URL")


@pytest.mark.e2e
def test_api_health_smoke():
    base_url = _get_base_url()
    if not base_url:
        pytest.skip("LAB_LENS_API_URL (or SERVICE_URL) is not set")

    resp = requests.get(f"{base_url.rstrip('/')}/health", timeout=15)
    assert resp.status_code == 200

    # Should be JSON and include a status indicator.
    payload = resp.json()
    assert "status" in payload


@pytest.mark.e2e
def test_api_info_smoke():
    base_url = _get_base_url()
    if not base_url:
        pytest.skip("LAB_LENS_API_URL (or SERVICE_URL) is not set")

    resp = requests.get(f"{base_url.rstrip('/')}/info", timeout=15)
    assert resp.status_code == 200
