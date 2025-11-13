from __future__ import annotations

import os
from typing import Dict, Tuple

import requests


def deploy_rule_via_mcp(rule_code: str, *, rule_name: str, metadata: Dict[str, str] | None = None) -> Tuple[bool, str]:
    """Send the generated rule to the openHAB MCP server, if configured.

    The MCP server endpoint is discovered via OPENHAB_MCP_URL. An optional bearer token
    can be supplied through OPENHAB_STAGING_TOKEN or OPENHAB_MCP_TOKEN.
    """
    base_url = os.environ.get("OPENHAB_MCP_URL")
    if not base_url:
        return False, "OPENHAB_MCP_URL is not configured."

    endpoint = base_url.rstrip("/") + "/deploy-rule"
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("OPENHAB_MCP_TOKEN") or os.environ.get("OPENHAB_STAGING_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "rule_name": rule_name,
        "rule_code": rule_code,
        "metadata": metadata or {},
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        return False, f"Failed to reach MCP server: {exc}"

    try:
        data = response.json()
    except ValueError:
        return True, response.text

    status = str(data.get("status", "")).lower()
    message = str(data.get("message", response.text))
    success = status in ("", "ok", "success", "deployed")
    return success, message


