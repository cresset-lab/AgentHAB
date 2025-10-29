import os
from typing import List, Dict, Any

import requests


class OpenHABAPI:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = base_url or os.environ.get("OPENHAB_URL", "http://localhost:8080")
        self.token = token or os.environ.get("OPENHAB_TOKEN")

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def list_items(self) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/rest/items", headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_item(self, name: str) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/rest/items/{name}", headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()






