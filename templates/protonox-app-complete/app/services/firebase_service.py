import time
from typing import Any, Dict, Optional

import requests

from ..firebase.firebase_config import FIREBASE_CONFIG


class FirebaseAuthError(Exception):
    pass


class FirebaseService:
    """Firebase REST helper for Auth, Firestore, and Storage."""

    def __init__(self):
        self.session = requests.Session()
        self.id_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: float = 0

    # -------------------- Auth --------------------
    def register(self, email: str, password: str) -> Dict[str, Any]:
        return self._identity_call("signUp", {"email": email, "password": password, "returnSecureToken": True})

    def login(self, email: str, password: str) -> Dict[str, Any]:
        data = self._identity_call("signInWithPassword", {"email": email, "password": password, "returnSecureToken": True})
        self._store_tokens(data)
        return data

    def logout(self) -> None:
        self.id_token = None
        self.refresh_token = None
        self.token_expiry = 0

    def refresh_session(self) -> Optional[str]:
        if not self.refresh_token:
            return None
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        url = f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_CONFIG['apiKey']}"
        resp = self.session.post(url, data=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        self.id_token = data.get("id_token")
        self.refresh_token = data.get("refresh_token")
        self.token_expiry = time.time() + int(data.get("expires_in", 3600))
        return self.id_token

    def validate_token(self) -> bool:
        if not self.id_token:
            return False
        if time.time() >= self.token_expiry - 60:
            self.refresh_session()
        return bool(self.id_token)

    def _identity_call(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={FIREBASE_CONFIG['apiKey']}"
        resp = self.session.post(url, json=payload, timeout=15)
        if not resp.ok:
            raise FirebaseAuthError(resp.text)
        return resp.json()

    def _store_tokens(self, data: Dict[str, Any]) -> None:
        self.id_token = data.get("idToken")
        self.refresh_token = data.get("refreshToken")
        self.token_expiry = time.time() + int(data.get("expiresIn", 3600))

    # -------------------- Firestore --------------------
    def firestore_get(self, document_path: str) -> Dict[str, Any]:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}/databases/(default)/documents/{document_path}"
        resp = self.session.get(url, headers=self._auth_header(), timeout=15)
        resp.raise_for_status()
        return resp.json()

    def firestore_set(self, document_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}/databases/(default)/documents/{document_path}"
        resp = self.session.patch(url, headers=self._auth_header(), json={"fields": self._to_firestore_fields(data)}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # -------------------- Storage --------------------
    def storage_upload(self, bucket_path: str, file_bytes: bytes, content_type: str = "application/octet-stream") -> Dict[str, Any]:
        url = f"https://firebasestorage.googleapis.com/v0/b/{FIREBASE_CONFIG['storageBucket']}/o?uploadType=media&name={bucket_path}"
        headers = self._auth_header()
        headers["Content-Type"] = content_type
        resp = self.session.post(url, headers=headers, data=file_bytes, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # -------------------- Helpers --------------------
    def _auth_header(self) -> Dict[str, str]:
        if not self.validate_token():
            raise FirebaseAuthError("User not authenticated")
        return {"Authorization": f"Bearer {self.id_token}"}

    def _to_firestore_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Basic JSON to Firestore field transformation for primitive types
        fields: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, bool):
                fields[key] = {"booleanValue": value}
            elif isinstance(value, int):
                fields[key] = {"integerValue": value}
            elif isinstance(value, float):
                fields[key] = {"doubleValue": value}
            else:
                fields[key] = {"stringValue": str(value)}
        return fields
