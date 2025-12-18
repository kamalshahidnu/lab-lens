import os

import pytest
import requests


def _get_base_url() -> str | None:
    return os.getenv("LAB_LENS_WEB_URL") or os.getenv("SERVICE_URL")


@pytest.mark.e2e
def test_streamlit_health_smoke():
    base_url = _get_base_url()
    if not base_url:
        pytest.skip("LAB_LENS_WEB_URL (or SERVICE_URL) is not set")

    resp = requests.get(f"{base_url.rstrip('/')}/_stcore/health", timeout=15)
    assert resp.status_code == 200


@pytest.mark.e2e
def test_streamlit_homepage_smoke():
    base_url = _get_base_url()
    if not base_url:
        pytest.skip("LAB_LENS_WEB_URL (or SERVICE_URL) is not set")

    resp = requests.get(f"{base_url.rstrip('/')}/", timeout=30, allow_redirects=True)
    assert resp.status_code == 200
