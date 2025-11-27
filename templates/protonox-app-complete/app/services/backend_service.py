import logging
from typing import Any, Dict, Optional

import requests

API_BASE_URL = "https://your-backend.onrender.com"


class BackendService:
    """HTTP client for Render-hosted FastAPI backends with retry support."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.logger = logging.getLogger("BackendService")

    def get(self, path: str, token: Optional[str] = None, retries: int = 2) -> Dict[str, Any]:
        return self._request("GET", path, token=token, retries=retries)

    def post(self, path: str, payload: Dict[str, Any], token: Optional[str] = None, retries: int = 2) -> Dict[str, Any]:
        return self._request("POST", path, json=payload, token=token, retries=retries)

    def put(self, path: str, payload: Dict[str, Any], token: Optional[str] = None, retries: int = 2) -> Dict[str, Any]:
        return self._request("PUT", path, json=payload, token=token, retries=retries)

    def delete(self, path: str, token: Optional[str] = None, retries: int = 2) -> Dict[str, Any]:
        return self._request("DELETE", path, token=token, retries=retries)

    def _request(self, method: str, path: str, token: Optional[str] = None, retries: int = 2, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = kwargs.pop("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        attempt = 0
        while True:
            try:
                resp = self.session.request(method, url, headers=headers, timeout=15, **kwargs)
                if resp.status_code >= 500 and attempt < retries:
                    attempt += 1
                    self.logger.warning("Retrying %s %s (%s)", method, url, resp.status_code)
                    continue
                resp.raise_for_status()
                if resp.text:
                    return resp.json()
                return {}
            except requests.RequestException as exc:
                if attempt < retries:
                    attempt += 1
                    self.logger.warning("Retrying due to error: %s", exc)
                    continue
                raise
