# --- utils/local_llm.py ---
import requests, os, typing as t
from utils.logger import logger

BASE_URL = "http://192.168.20.31:1234/v1/chat/completions"
DEFAULT_MODEL = os.getenv("LLM_MODEL", "mistralai/devstral-small-2507")

def call_llm(prompt: str, *, model: str | None = None,
             temperature: float = 0.0, max_tokens: int = 1024) -> str:
    m = model or DEFAULT_MODEL
    logger.debug("LLM call | model={} temp={} max_tokens={}", m, temperature, max_tokens)

    payload = {
        "model": m,
        "messages": [
            {"role": "user", "content": prompt},   # רק user, system prompt מוגדר ב-LM Studio!
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    try:
        r = requests.post(BASE_URL, json=payload, timeout=300)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        logger.debug("LLM response len={} chars", len(content))
        return content
    except Exception as e:
        logger.error("LLM request failed: {}", e)
        raise RuntimeError("LLM call failed") from e
