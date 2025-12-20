from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token as google_id_token

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class GoogleOAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str


def load_google_oauth_config() -> Optional[GoogleOAuthConfig]:
    client_id = (os.getenv("GOOGLE_OAUTH_CLIENT_ID") or "").strip()
    client_secret = (os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") or "").strip()
    redirect_uri = (os.getenv("GOOGLE_OAUTH_REDIRECT_URI") or "").strip()
    if not (client_id and client_secret and redirect_uri):
        return None
    return GoogleOAuthConfig(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * ((4 - (len(data) % 4)) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("utf-8"))


def _sign_state(payload: Dict[str, Any], secret: str) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    return f"{_b64url(body)}.{_b64url(sig)}"


def verify_state(state: str, secret: str, *, max_age_seconds: int = 10 * 60) -> Optional[Dict[str, Any]]:
    try:
        body_b64, sig_b64 = state.split(".", 1)
        body = _b64url_decode(body_b64)
        sig = _b64url_decode(sig_b64)
        expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(body.decode("utf-8"))
        ts = int(payload.get("ts", 0))
        if ts <= 0:
            return None
        if int(time.time()) - ts > max_age_seconds:
            return None
        return payload
    except Exception:
        return None


def build_authorize_url(cfg: GoogleOAuthConfig, *, prompt: str = "select_account") -> str:
    """
    Create a Google OAuth 2.0 authorization URL (server-side code flow).

    We sign state with the client_secret so we can validate callback without relying on Streamlit session state.
    """
    state_payload = {"ts": int(time.time())}
    state = _sign_state(state_payload, cfg.client_secret)

    params = {
        "client_id": cfg.client_id,
        "redirect_uri": cfg.redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "include_granted_scopes": "true",
        "prompt": prompt,
        "state": state,
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def exchange_code_for_tokens(cfg: GoogleOAuthConfig, code: str) -> Dict[str, Any]:
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": cfg.client_id,
            "client_secret": cfg.client_secret,
            "redirect_uri": cfg.redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def verify_google_id_token(id_token_str: str, *, client_id: str) -> Dict[str, Any]:
    # Verifies signature + audience + expiry (fetches Google public certs at runtime).
    req = GoogleAuthRequest()
    claims = google_id_token.verify_oauth2_token(id_token_str, req, audience=client_id)
    return dict(claims)


def fetch_userinfo(access_token: str) -> Dict[str, Any]:
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
