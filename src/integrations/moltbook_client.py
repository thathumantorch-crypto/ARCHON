"""Moltbook integration helpers.

Provides registration, heartbeat tracking, and convenience helpers so ARCHON
can participate in the Moltbook community without hard-coding credentials.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Optional, Any

import requests


@dataclass
class MoltbookCredentials:
    api_key: Optional[str] = None
    agent_name: Optional[str] = None
    description: Optional[str] = None
    claim_url: Optional[str] = None
    verification_code: Optional[str] = None


class MoltbookClient:
    """Lightweight client for Moltbook registration + heartbeat."""

    BASE_URL = "https://www.moltbook.com/api/v1"
    HEARTBEAT_URL = "https://www.moltbook.com/heartbeat.md"
    CREDENTIAL_STORE = Path.home() / ".config/moltbook/credentials.json"
    STATE_FILE = Path("memory/moltbook_state.json")
    HEARTBEAT_INTERVAL = timedelta(minutes=30)
    POST_CONSIDERATION_INTERVAL = timedelta(hours=1)

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()
        self.credentials = MoltbookCredentials(
            api_key=os.getenv("MOLTBOOK_API_KEY"),
            agent_name=os.getenv("MOLTBOOK_AGENT_NAME"),
            description=os.getenv("MOLTBOOK_AGENT_DESCRIPTION"),
        )
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._load_credentials_from_disk()

    # ------------------------------------------------------------------
    # Credential helpers
    # ------------------------------------------------------------------
    def _load_credentials_from_disk(self) -> None:
        if self.CREDENTIAL_STORE.exists():
            try:
                data = json.loads(self.CREDENTIAL_STORE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return
            self.credentials.api_key = self.credentials.api_key or data.get("api_key")
            self.credentials.agent_name = self.credentials.agent_name or data.get("agent_name")
            self.credentials.description = self.credentials.description or data.get("description")
            self.credentials.claim_url = data.get("claim_url")
            self.credentials.verification_code = data.get("verification_code")

    def _save_credentials_to_disk(self) -> None:
        self.CREDENTIAL_STORE.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "api_key": self.credentials.api_key,
            "agent_name": self.credentials.agent_name,
            "description": self.credentials.description,
            "claim_url": self.credentials.claim_url,
            "verification_code": self.credentials.verification_code,
        }
        self.CREDENTIAL_STORE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def is_registered(self) -> bool:
        return bool(self.credentials.api_key)

    def ensure_registration(self, agent_name: str, description: str) -> Dict[str, Any]:
        if self.is_registered():
            return {
                "registered": True,
                "already_registered": True,
                "claim_url": self.credentials.claim_url,
                "verification_code": self.credentials.verification_code,
                "message": "API key already stored.",
            }
        return self.register_agent(agent_name, description)

    def register_agent(self, agent_name: str, description: str) -> Dict[str, Any]:
        payload = {"name": agent_name, "description": description}
        url = f"{self.BASE_URL}/agents/register"
        response = self.session.post(url, json=payload, timeout=30)
        response.raise_for_status()
        body = response.json()
        agent = body.get("agent", {})

        self.credentials = MoltbookCredentials(
            api_key=agent.get("api_key"),
            agent_name=agent_name,
            description=description,
            claim_url=agent.get("claim_url"),
            verification_code=agent.get("verification_code"),
        )
        self._save_credentials_to_disk()

        return {
            "registered": True,
            "claim_url": self.credentials.claim_url,
            "verification_code": self.credentials.verification_code,
            "message": "Agent registered. Share claim URL with your human.",
        }

    def check_claim_status(self) -> Dict[str, Any]:
        resp = self._authorized_get("/agents/status")
        return resp.json()

    def get_profile(self) -> Dict[str, Any]:
        resp = self._authorized_get("/agents/me")
        return resp.json()

    def get_feed(self, sort: str = "hot", limit: int = 25, cursor: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"sort": sort, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        resp = self._authorized_get("/posts", params=params)
        return resp.json()

    def get_post(self, post_id: str) -> Dict[str, Any]:
        resp = self._authorized_get(f"/posts/{post_id}")
        return resp.json()

    def get_comments(self, post_id: str, sort: str = "top") -> Dict[str, Any]:
        params = {"sort": sort}
        resp = self._authorized_get(f"/posts/{post_id}/comments", params=params)
        return resp.json()

    def create_post(self, submolt_name: str, title: str, content: str, url: Optional[str] = None) -> Dict[str, Any]:
        if not self.credentials.api_key:
            raise RuntimeError("Moltbook API key not available. Register first.")
        payload: Dict[str, Any] = {"submolt_name": submolt_name, "title": title, "content": content}
        if url:
            payload["url"] = url
        headers = {
            "Authorization": f"Bearer {self.credentials.api_key}",
            "Content-Type": "application/json",
        }
        resp = self.session.post(f"{self.BASE_URL}/posts", json=payload, headers=headers, timeout=30)
        if not resp.ok:
            detail = self._extract_error_detail(resp)
            raise requests.HTTPError(f"Moltbook post failed: {resp.status_code} {detail}", response=resp)
        resp.raise_for_status()
        self.record_post_consideration(posted=True)
        return resp.json()

    def create_comment(self, post_id: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.credentials.api_key:
            raise RuntimeError("Moltbook API key not available. Register first.")
        payload: Dict[str, Any] = {"content": content}
        if parent_id:
            payload["parent_id"] = parent_id
        headers = {
            "Authorization": f"Bearer {self.credentials.api_key}",
            "Content-Type": "application/json",
        }
        resp = self.session.post(
            f"{self.BASE_URL}/posts/{post_id}/comments",
            json=payload,
            headers=headers,
            timeout=30,
        )
        if not resp.ok:
            detail = self._extract_error_detail(resp)
            raise requests.HTTPError(f"Moltbook comment failed: {resp.status_code} {detail}", response=resp)
        resp.raise_for_status()
        return resp.json()

    def like_post(self, post_id: str) -> Dict[str, Any]:
        if not self.credentials.api_key:
            raise RuntimeError("Moltbook API key not available. Register first.")
        headers = {"Authorization": f"Bearer {self.credentials.api_key}"}
        resp = self.session.post(
            f"{self.BASE_URL}/posts/{post_id}/like",
            headers=headers,
            timeout=20,
        )
        if not resp.ok:
            detail = self._extract_error_detail(resp)
            raise requests.HTTPError(f"Moltbook like failed: {resp.status_code} {detail}", response=resp)
        resp.raise_for_status()
        return resp.json()

    def _extract_error_detail(self, response: requests.Response) -> str:
        try:
            data = response.json()
            if isinstance(data, dict):
                return data.get('message') or data.get('error') or response.text
        except ValueError:
            pass
        return response.text

    def get_state(self) -> Dict[str, Any]:
        state = self._load_state()
        last_check = state.get("lastMoltbookCheck")
        due = self._heartbeat_due(last_check)
        post_due = self._post_interval_due(state.get("lastPostConsideration"))
        return {
            "registered": self.is_registered(),
            "agent_name": self.credentials.agent_name,
            "description": self.credentials.description,
            "claim_url": self.credentials.claim_url,
            "verification_code": self.credentials.verification_code,
            "last_check": last_check,
            "heartbeat_due": due,
            "last_post_consideration": state.get("lastPostConsideration"),
            "last_post_timestamp": state.get("lastPostTimestamp"),
            "post_consideration_due": post_due,
        }

    def perform_heartbeat_check(self, force: bool = False) -> Dict[str, Any]:
        state = self._load_state()
        last_check = state.get("lastMoltbookCheck")
        if not force and not self._heartbeat_due(last_check):
            return {
                "performed": False,
                "message": "Heartbeat recently performed",
                "last_check": last_check,
            }

        response = self.session.get(self.HEARTBEAT_URL, timeout=20)
        response.raise_for_status()
        timestamp = datetime.now(timezone.utc).isoformat()
        state["lastMoltbookCheck"] = timestamp
        self._save_state(state)
        return {
            "performed": True,
            "instructions": response.text,
            "last_check": timestamp,
        }

    def post_consideration_due(self) -> bool:
        state = self._load_state()
        return self._post_interval_due(state.get("lastPostConsideration"))

    def record_post_consideration(self, posted: bool = False) -> Dict[str, Any]:
        state = self._load_state()
        timestamp = datetime.now(timezone.utc).isoformat()
        state["lastPostConsideration"] = timestamp
        if posted:
            state["lastPostTimestamp"] = timestamp
        self._save_state(state)
        return state

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _authorized_get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        if not self.credentials.api_key:
            raise RuntimeError("Moltbook API key not available. Register first.")
        headers = {"Authorization": f"Bearer {self.credentials.api_key}"}
        url = f"{self.BASE_URL}{path}"
        response = self.session.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response

    def _load_state(self) -> Dict[str, Any]:
        if self.STATE_FILE.exists():
            try:
                return json.loads(self.STATE_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {
            "lastMoltbookCheck": None,
            "lastPostConsideration": None,
            "lastPostTimestamp": None,
        }

    def _save_state(self, data: Dict[str, Any]) -> None:
        self.STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _heartbeat_due(self, last_check_iso: Optional[str]) -> bool:
        if not last_check_iso:
            return True
        try:
            last = datetime.fromisoformat(last_check_iso)
        except ValueError:
            return True
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - last >= self.HEARTBEAT_INTERVAL

    def _post_interval_due(self, last_check_iso: Optional[str]) -> bool:
        if not last_check_iso:
            return True
        try:
            last = datetime.fromisoformat(last_check_iso)
        except ValueError:
            return True
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - last >= self.POST_CONSIDERATION_INTERVAL
