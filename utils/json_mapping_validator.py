# utils/json_mapping_validator.py
import re
from typing import Dict, Tuple

SAFE_KEY_RE = re.compile(r"^[A-Za-z0-9_\-\/]+$")  # allow nested paths like pages/login_page
ALLOWED_PREFIXES = ("pages/", "tests/", "conftest", "tests/conftest")

def _has_allowed_prefix(key: str) -> bool:
    if key == "conftest" or key == "tests/conftest":
        return True
    return key.startswith("pages/") or key.startswith("tests/")

def validate_code_mapping(obj) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Validate that 'obj' is a mapping: filename_without_ext -> python_code_string.
    Returns (clean_map, problems_map).
    Rules:
      - keys: non-empty str, only [A-Za-z0-9_-/], no leading slash, no '..'
      - keys must be under allowed prefixes: 'pages/', 'tests/', 'conftest', 'tests/conftest'
      - values: non-empty str
    """
    clean: Dict[str, str] = {}
    problems: Dict[str, str] = {}

    if not isinstance(obj, dict):
        problems["__root__"] = "not a dict"
        return {}, problems

    for k, v in obj.items():
        if not isinstance(k, str):
            problems[str(k)] = "key is not str"
            continue
        key = k.strip()
        if not key:
            problems[k] = "empty key"
            continue
        if key.startswith("/") or ".." in key:
            problems[key] = "unsafe path"
            continue
        if not SAFE_KEY_RE.match(key):
            problems[key] = "invalid chars in key (allowed: A-Z a-z 0-9 _ - /)"
            continue
        if not _has_allowed_prefix(key):
            problems[key] = "disallowed path (allowed prefixes: pages/, tests/, conftest)"
            continue
        if not isinstance(v, str):
            problems[key] = "value is not str"
            continue
        if not v.strip():
            problems[key] = "empty code string"
            continue
        clean[key] = v

    return clean, problems
