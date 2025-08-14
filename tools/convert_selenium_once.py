#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from agents.pom_converter_agent import POMConverterAgent

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
)

def iter_py_files(p: Path):
    if p.is_file() and p.suffix == ".py":
        yield p
    elif p.is_dir():
        for f in sorted(p.rglob("*.py")):
            yield f
    else:
        raise FileNotFoundError(f"Input path not found or not a .py file/dir: {p}")

def main() -> int:
    ap = argparse.ArgumentParser(description="Convert Selenium → Playwright (single run)")
    ap.add_argument("--in", dest="in_path", required=True, help="Input .py file or directory with .py files")
    ap.add_argument("--out", dest="out_dir", required=True, help="Output root directory (will contain pages/, tests/)")
    args = ap.parse_args()

    in_path = Path(args.in_path).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    conv = POMConverterAgent()

    ok = 0
    bad = 0

    for src in iter_py_files(in_path):
        print(f"Converting {src.name}...")
        try:
            conv.convert(src_path=src, out_dir=out_dir)
            ok += 1
        except Exception as e:
            bad += 1
            log.exception("❌ Exception during conversion for %s", src.name)
            # לא כותבים status.py/error.py כדי לא ללכלך את הפלט – נשאיר נקי לפי המדיניות
            print(f"❌ Conversion failed for {src.name}")

    print(f"Done. Success: {ok}, Failed: {bad}")
    return 0 if bad == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
