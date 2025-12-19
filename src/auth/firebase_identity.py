from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class FirebaseAuthResult:
    id_token: str
    refresh_token: Optional[str] = None
    local_id: Optional[str] = None
    email: Optional[str] = None


class FirebaseIdentityError(RuntimeError):
    pass


def _api_key() -> str:
    key = (os.getenv("FIREBASE_API_KEY") or "").strip()
    if not key:
        raise FirebaseIdentityError("FIREBASE_API_KEY is not set")
    return key


def _post(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"https://identitytoolkit.googleapis.com/v1/{endpoint}?key={_api_key()}"
    try:
        resp = requests.post(url, json=payload, timeout=15)
    except Exception as e:
        raise FirebaseIdentityError(f"Network error calling Firebase: {e}") from e

    data: Dict[str, Any] = {}
    try:
        data = resp.json() if resp.content else {}
    except Exception:
        data = {}

    if resp.status_code >= 400:
        # Typical shape: {"error": {"message":"EMAIL_NOT_FOUND", ...}}
        msg = (
            str((data.get("error") or {}).get("message") or resp.text or f"HTTP {resp.status_code}")
        ).strip()
        raise FirebaseIdentityError(msg)

    return data


def sign_in_with_email_password(email: str, password: str) -> FirebaseAuthResult:
    data = _post(
        "accounts:signInWithPassword",
        {"email": email, "password": password, "returnSecureToken": True},
    )
    return FirebaseAuthResult(
        id_token=str(data.get("idToken") or ""),
        refresh_token=data.get("refreshToken"),
        local_id=data.get("localId"),
        email=data.get("email"),
    )


def sign_up_with_email_password(email: str, password: str) -> FirebaseAuthResult:
    data = _post(
        "accounts:signUp",
        {"email": email, "password": password, "returnSecureToken": True},
    )
    return FirebaseAuthResult(
        id_token=str(data.get("idToken") or ""),
        refresh_token=data.get("refreshToken"),
        local_id=data.get("localId"),
        email=data.get("email"),
    )

