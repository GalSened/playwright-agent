#!/usr/bin/env python3
from __future__ import annotations
import os, json, time, logging
from typing import Any, Dict, List, Optional
import requests

log = logging.getLogger(__name__)

OPENAI_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_KEY  = os.getenv("OPENAI_API_KEY", "")

class OpenAIClient:
    def __init__(self) -> None:
        if not OPENAI_KEY:
            raise EnvironmentError("OPENAI_API_KEY is not set.")
        self.base = OPENAI_BASE.rstrip("/")

    def call_chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 2048,
        json_mode: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
        timeout_s: int = 120,
        retries: int = 3,
    ) -> str:
        """
        Returns raw string content from .choices[0].message.
        Enforces Structured Output if json_schema is provided; else JSON mode if json_mode=True.
        Never sends legacy params (no temperature/top_p/modalities/reasoning).
        """
        url = f"{self.base}/chat/completions"

        # Build payload according to modern Chat Completions
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": int(max_tokens),
            # no temperature/top_p to avoid 400 on GPT-5 family defaults
        }

        if json_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": json_schema,
            }
        elif json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json",
        }

        backoff = 1.0
        last_err: Optional[Exception] = None

        for attempt in range(1, retries + 1):
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
                if r.status_code == 429:
                    # rate limit – simple backoff
                    log.warning("Rate limited (429). Sleeping for %.2fs", backoff)
                    time.sleep(backoff)
                    backoff = min(backoff * 1.7, 15.0)
                    continue
                r.raise_for_status()
                data = r.json()

                # Prefer parsed (Structured Outputs)
                choices = data.get("choices", [])
                if not choices:
                    raise ValueError("No choices in response")

                msg = choices[0].get("message", {}) or {}
                if "parsed" in msg and msg["parsed"] is not None:
                    return json.dumps(msg["parsed"], ensure_ascii=False)

                content = msg.get("content", "")
                if content is None:
                    content = ""
                content = str(content)

                if not content.strip():
                    # If we enforced json_schema, content can be empty while parsed exists.
                    # If still empty – try one more time with shorter system.
                    raise ValueError("Empty content from model")
                return content
            except Exception as e:
                last_err = e
                log.debug("OpenAI call failed (attempt %s): %s", attempt, e)
                time.sleep(backoff)
                backoff = min(backoff * 1.7, 10.0)

        # Out of retries:
        if isinstance(last_err, requests.HTTPError):
            try:
                err_body = last_err.response.text  # type: ignore[attr-defined]
            except Exception:
                err_body = str(last_err)
            raise RuntimeError(f"OpenAI error {last_err.response.status_code}: {err_body}")  # type: ignore[attr-defined]
        raise RuntimeError(f"OpenAI call failed after {retries} attempts: {last_err}")

llm_client = OpenAIClient()
