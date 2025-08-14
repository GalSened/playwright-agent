#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any

from utils.openai_llm import llm_client

logger = logging.getLogger(__name__)

ALLOWED_PREFIXES = ("pages/", "tests/", "tests/conftest", "conftest")

# ===== System Prompts =====
SYS_ANALYZER = (
    "You are a strict code-to-code converter.\n"
    "Input is one Python file: either a Selenium PageObject or a Selenium pytest test.\n"
    "Your job: output ONLY a single JSON object mapping output file KEYS to Python code STRINGS.\n"
    "Allowed KEYS MUST start with 'pages/' or 'tests/' (or 'tests/conftest' or 'conftest').\n"
    "Do NOT include file extensions in KEYS (the tool will add .py).\n"
    "If input is a PageObject — emit 1+ 'pages/*' files and 0+ 'tests/*' that use them.\n"
    "If input is a Selenium test — emit equivalent Playwright pytest tests under 'tests/*' and any needed 'pages/*'.\n"
    "Use Playwright Python sync API, pytest style, stable selectors (prefer page.locator), NO sleeps.\n"
    "Return ONLY the JSON object. No explanations. No Markdown. No backticks."
)

SYS_BUILDER = (
    "You receive an initial JSON mapping of files-to-code.\n"
    "Refine and finalize it for Playwright Python/pytest.\n"
    "IMPORTANT: Keep keys only under pages/* or tests/* (or tests/conftest / conftest), no extensions.\n"
    "Return ONLY the JSON object. No explanations. No Markdown. No backticks."
)

# ===== JSON extraction helpers =====
def _parse_json_loose(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("empty response")
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.I)
        s = re.sub(r"\s*```$", "", s)
    if s.startswith("{") and s.endswith("}"):
        return json.loads(s)
    start = s.find("{")
    if start == -1:
        raise ValueError("no JSON object found")
    best = None
    depth = 0
    cand_start = start
    for i in range(start, len(s)):
        c = s[i]
        if c == "{":
            if depth == 0:
                cand_start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                best = s[cand_start:i+1]
    if not best:
        raise ValueError("unbalanced JSON braces")
    return json.loads(best)

def _ensure_valid_keys(mapping: Dict[str, str]) -> None:
    bad = [k for k in mapping.keys() if not any(k == p or k.startswith(p) for p in ALLOWED_PREFIXES)]
    if bad:
        raise ValueError(
            "Disallowed keys found: " + ", ".join(bad)
            + " | Allowed keys MUST start with 'pages/' or 'tests/' (or 'tests/conftest' / 'conftest'). "
        )

def _save_mapping(out_dir: Path, mapping: Dict[str, str]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, code in mapping.items():
        key = key.strip().lstrip("/")
        if not key.endswith(".py"):
            key = f"{key}.py"
        dest = out_dir / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(code, encoding="utf-8")
        logger.info("Saved: %s", dest)

# ===== Structured Output schema (strict!) =====
FILEMAP_SCHEMA: Dict[str, Any] = {
    "name": "file_map",
    "schema": {
        "type": "object",
        "description": "Mapping from file key to Python module text.",
        "additionalProperties": False,
        "patternProperties": {
            r"^(pages\/[^\/]+(?:\/[^\/]+)*)$": {"type": "string"},
            r"^(tests\/[^\/]+(?:\/[^\/]+)*)$": {"type": "string"},
            r"^(tests\/conftest)$": {"type": "string"},
            r"^(conftest)$": {"type": "string"},
        },
        "maxProperties": 40
    },
    "strict": True
}

def _call_json_strict(model: str, system_prompt: str, user_prompt: str, max_tokens: int) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Attempt 1: Structured Outputs (json_schema)
    raw = llm_client.call_chat(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        json_schema=FILEMAP_SCHEMA,
    )
    try:
        return _parse_json_loose(raw)
    except Exception as e:
        logger.error("Model returned non-JSON (schema mode): %s", e)

    # Attempt 2: JSON mode with an explicit reminder
    rescue_messages = messages + [
        {"role": "user", "content": "Return ONLY a pure JSON object as specified. No other text."}
    ]
    raw2 = llm_client.call_chat(
        model=model,
        messages=rescue_messages,
        max_tokens=max_tokens,
        json_mode=True,
    )
    return _parse_json_loose(raw2)

class POMConverterAgent:
    def __init__(self) -> None:
        self.model_analyzer = os.getenv("OPENAI_MODEL_ANALYZER", "gpt-5-mini")
        self.model_builder  = os.getenv("OPENAI_MODEL_BUILDER",  "gpt-5")
        self.max_tokens = int(os.getenv("OPENAI_MAX_COMPLETION_TOKENS", "4096"))
        logger.info("MODELS: %s %s | max_tokens=%s", self.model_analyzer, self.model_builder, self.max_tokens)

    def _make_user_prompt(self, src_path: Path, code: str) -> str:
        name = src_path.name
        return (
            "Convert the following single Python file from Selenium to Playwright.\n"
            f"Filename: {name}\n\n"
            "=== INPUT CODE START ===\n"
            f"{code}\n"
            "=== INPUT CODE END ===\n"
            "Output strictly as a JSON object mapping file keys to full Python modules (strings). "
            "Keys must be: pages/* or tests/* (or tests/conftest or conftest), without '.py'."
        )

    def convert(self, src_path: Path, out_dir: Path) -> Dict[str, Any]:
        src_path = Path(src_path)
        out_dir = Path(out_dir)
        logger.debug("POMConverterAgent: Starting conversion for %s -> %s", src_path, out_dir)

        code = src_path.read_text(encoding="utf-8")
        user_prompt = self._make_user_prompt(src_path, code)

        # Analyzer (already returns mapping)
        logger.debug("Analyzer call…")
        mapping = _call_json_strict(
            model=self.model_analyzer,
            system_prompt=SYS_ANALYZER,
            user_prompt=user_prompt,
            max_tokens=self.max_tokens,
        )

        # Builder (refines mapping)
        logger.debug("Builder call…")
        builder_user = (
            "You receive an initial JSON mapping of files-to-code. "
            "Refine and finalize it for Playwright Python/pytest. "
            "IMPORTANT: Keep only pages/* or tests/* (or tests/conftest / conftest), no extensions.\n\n"
            "=== CURRENT MAPPING (JSON) ===\n"
            f"{json.dumps(mapping, ensure_ascii=False)}\n"
            "=== END ==="
        )
        final_mapping = _call_json_strict(
            model=self.model_builder,
            system_prompt=SYS_BUILDER,
            user_prompt=builder_user,
            max_tokens=self.max_tokens,
        )

        _ensure_valid_keys(final_mapping)
        _save_mapping(out_dir, final_mapping)
        return final_mapping
