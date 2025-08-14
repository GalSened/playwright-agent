#!/usr/bin/env bash
set -euo pipefail

echo "== Build image =="
docker compose build --no-cache playwright-agent

echo "== Run conversion inside container =="
docker compose run --rm \
  -e OPENAI_API_KEY="${OPENAI_API_KEY:?OPENAI_API_KEY is not set}" \
  -e OPENAI_MAX_COMPLETION_TOKENS="${OPENAI_MAX_COMPLETION_TOKENS:-2048}" \
  -e OPENAI_MODEL_ANALYZER="gpt-5-mini" \
  -e OPENAI_MODEL_ENFORCER="gpt-5-mini" \
  -e OPENAI_MODEL_BUILDER="gpt-5" \
  playwright-agent /bin/bash -s <<'IN'
set -euo pipefail

# Sanity: המודלים והטקסטים שה-agent טוען
python - <<'PY'
from agents.pom_converter_agent import MODEL_ANALYZER, MODEL_ENFORCER, MODEL_BUILDER, SYS_ANALYZER
from utils.json_mapping_validator import ALLOWED_PREFIXES
print("MODELS:", MODEL_ANALYZER, MODEL_ENFORCER, MODEL_BUILDER)
print("ALLOWED_PREFIXES:", ALLOWED_PREFIXES)
print("HAS_ALLOWED_KEYS_TEXT:", "Allowed keys MUST start with 'pages/'" in SYS_ANALYZER)
PY

# ניקוי פלט קודם
rm -rf tests/generated/login/*

# המרה בפועל
python tools/convert_selenium_once.py --in selenium_tests/login --out tests/generated/login

# הצגת קבצים
echo "--- FILES ---"
find tests/generated/login -maxdepth 3 -type f -name "*.py" -print | sort

# ולידציה: רק pages/, tests/, conftest מותר
echo "--- VALIDATION ---"
BAD=$(find tests/generated/login -type f -name "*.py" | grep -E -v '/(pages|tests)/|/conftest\.py$' || true)
if [ -n "$BAD" ]; then
  echo "❌ Disallowed files detected:"
  echo "$BAD"
  exit 1
else
  echo "✅ Output paths are valid (pages/ , tests/ , conftest only)"
fi
IN
