# utils/local_llm.py
import json
import logging
import os
import socket
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "DEBUG"),
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s - %(message)s",
)

DEFAULT_PORT = int(os.getenv("LLM_PORT", "1234"))
DEFAULT_TIMEOUT = float(os.getenv("LLM_TIMEOUT_SEC", "120"))
DEFAULT_RETRIES = int(os.getenv("LLM_RETRIES", "2"))  # total attempts = 1 + retries
DEFAULT_RETRY_BACKOFF_MS = int(os.getenv("LLM_RETRY_BACKOFF_MS", "500"))

ENV_BASE_URL = os.getenv("LLM_BASE_URL", "").strip().rstrip("/")
ENV_HOSTS = [h.strip() for h in os.getenv("LLM_HOSTS", "").split(",") if h.strip()]

def _candidate_hosts() -> List[str]:
    hosts: List[str] = []
    hosts.extend(ENV_HOSTS)
    if "host.docker.internal" not in hosts:
        hosts.append("host.docker.internal")
    if "localhost" not in hosts:
        hosts.append("localhost")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if primary_ip not in hosts:
            hosts.append(primary_ip)
    except Exception:
        pass
    seen = set()
    uniq: List[str] = []
    for h in hosts:
        if h not in seen:
            uniq.append(h)
            seen.add(h)
    return uniq

class LocalLLMClient:
    """
    Hardened client for OpenAI-compatible /v1 API (LM Studio, etc.).
    - Prefers LLM_BASE_URL; otherwise probes known hosts on DEFAULT_PORT.
    - Retries with backoff, rich logging.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        retry_backoff_ms: int = DEFAULT_RETRY_BACKOFF_MS,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._configured_base_url = (base_url or ENV_BASE_URL).rstrip("/") if (base_url or ENV_BASE_URL) else ""
        self._port = port
        self._timeout = timeout
        self._retries = max(0, retries)
        self._retry_backoff_ms = max(0, retry_backoff_ms)
        self._session = session or requests.Session()
        self._resolved_base_url: Optional[str] = None

    def health_check(self) -> Tuple[bool, Optional[str]]:
        try:
            base = self._ensure_base_url()
            return True, base
        except Exception as e:
            return False, str(e)

    def call_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        top_p: float = 0.1,
        max_tokens: int = 2048,
        extra_payload: Optional[Dict[str, Any]] = None,
        return_json: bool = False,
    ) -> Any:
        base = self._ensure_base_url()
        url = f"{base}/v1/chat/completions"
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        if extra_payload:
            payload.update(extra_payload)

        attempt = 0
        last_error: Optional[Exception] = None

        while True:
            attempt += 1
            try:
                logger.debug(
                    "LLM call | url=%s model=%s temp=%s top_p=%s max_tokens=%s attempt=%s",
                    url, model, temperature, top_p, max_tokens, attempt,
                )
                r = self._session.post(url, json=payload, timeout=self._timeout)
                logger.debug("LLM raw status=%s body=%s", r.status_code, self._safe_text(r))
                r.raise_for_status()

                data = r.json()
                content = self._extract_content(data)

                if return_json:
                    return data
                return content

            except Exception as e:
                last_error = e
                logger.error("LLM request failed on attempt %s: %s", attempt, e)
                if attempt > self._retries:
                    break
                self._sleep_backoff(attempt)

        raise RuntimeError(f"LLM call failed after {attempt} attempts: {last_error}")

    def _ensure_base_url(self) -> str:
        if self._resolved_base_url:
            return self._resolved_base_url

        candidates: List[str] = []
        if self._configured_base_url:
            candidates.append(self._configured_base_url.rstrip("/"))
        else:
            for h in _candidate_hosts():
                candidates.append(f"http://{h}:{self._port}")

        logger.debug("Probing LLM base URLs: %s", candidates)
        for base in candidates:
            try:
                if self._probe_models(base):
                    self._resolved_base_url = base.rstrip("/")
                    logger.info("LLM base URL resolved: %s", self._resolved_base_url)
                    return self._resolved_base_url
            except Exception as e:
                logger.debug("Probe failed for %s: %s", base, e)

        raise ConnectionError(
            f"Could not resolve a healthy LLM base URL. Tried: {candidates}. "
            f"Set LLM_BASE_URL or ensure your LM Studio server is reachable."
        )

    def _probe_models(self, base: str) -> bool:
        url = f"{base.rstrip('/')}/v1/models"
        r = self._session.get(url, timeout=min(self._timeout, 10.0))
        logger.debug("Probe /v1/models status=%s body=%s", r.status_code, self._safe_text(r))
        r.raise_for_status()
        try:
            j = r.json()
            return isinstance(j, dict) and "data" in j
        except Exception:
            return False

    @staticmethod
    def _extract_content(resp_json: Dict[str, Any]) -> str:
        choices = resp_json.get("choices") or []
        if not choices:
            raise ValueError(f"Invalid LLM response (no choices): {resp_json}")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if content is None:
            raise ValueError(f"LLM response missing 'content': {json.dumps(resp_json)[:2000]}")
        return content

    @staticmethod
    def _safe_text(r: requests.Response, limit: int = 2000) -> str:
        try:
            t = r.text
            if len(t) > limit:
                return t[:limit] + "...<truncated>"
            return t
        except Exception:
            return "<unreadable>"

    def _sleep_backoff(self, attempt: int) -> None:
        base_ms = max(100, self._retry_backoff_ms)
        sleep_ms = min(base_ms * (2 ** (attempt - 1)), 4000)
        time.sleep(sleep_ms / 1000.0)

llm_client = LocalLLMClient()
