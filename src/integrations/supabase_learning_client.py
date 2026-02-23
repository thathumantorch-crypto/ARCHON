"""Supabase-hosted knowledge API client for ARCHON."""
from __future__ import annotations

import json
from typing import List, Dict, Optional, Iterable

import requests


class SupabaseLearningClient:
    """Lightweight helper to call the provided Supabase edge function."""

    def __init__(self, api_url: str, api_key: str, session: Optional[requests.Session] = None) -> None:
        if not api_url:
            raise ValueError("Supabase API URL must be provided")
        if not api_key:
            raise ValueError("Supabase API key must be provided")
        self.api_url = api_url
        self.api_key = api_key
        self.session = session or requests.Session()

    def generate(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        """Send a chat-style request and aggregate the content."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {"messages": messages, "stream": stream}
        response = self.session.post(
            self.api_url,
            headers=headers,
            json=payload,
            stream=stream,
            timeout=60,
        )
        response.raise_for_status()

        if not stream:
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return ""
            delta = choices[0].get("message") or choices[0].get("delta") or {}
            return delta.get("content", "")

        # Streaming mode (Server-Sent Events style)
        chunks: List[str] = []
        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded == "data: [DONE]":
                break
            if decoded.startswith("data: "):
                try:
                    payload = json.loads(decoded[6:])
                except json.JSONDecodeError:
                    continue
                delta = payload.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content")
                if content:
                    chunks.append(content)
        return "".join(chunks)

    def run_prompt(self, prompt: str, system: Optional[str] = None) -> str:
        """Convenience wrapper for single user prompt."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.generate(messages, stream=False)
