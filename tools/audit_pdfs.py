#!/usr/bin/env python3
"""Audit SIM800 AT Command Manuals against the local YAML database."""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import pdfplumber
except ImportError:
    print("pip install pdfplumber", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / ".audit_cache"
CACHE_DIR.mkdir(exist_ok=True)

MANUALS = {
    "V1.01": "https://raw.githubusercontent.com/AliNazarvand/Package-Datasheet/main/SIM800%20Series_AT%20Command%20Manual_V1.01.pdf",
    "V1.10": "https://raw.githubusercontent.com/AliNazarvand/Package-Datasheet/main/SIM800%20Series_AT%20Command%20Manual_V1.10.pdf",
    "V1.12": "https://raw.githubusercontent.com/AliNazarvand/Package-Datasheet/main/SIM800%20Series_AT%20Command%20Manual_V1.12.pdf",
}

SECTION_RE = re.compile(r"^\s*(\d+\.\d+\.\d+)\s+((?:AT\+?[A-Za-z0-9_]+|A/|\+\+\+))\b", re.MULTILINE)
TOKEN_RE = re.compile(r"\bAT\+[A-Z][A-Z0-9_]{1,20}\b")


def download(ver, url):
    dest = CACHE_DIR / (ver + ".pdf")
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    print("  downloading " + ver + " ...", file=sys.stderr)
    urllib.request.urlretrieve(url, dest)
    return dest


def scan_pdf(path):
    sections = {}
    tokens = {}
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            for m in SECTION_RE.finditer(text):
                sec, name = m.group(1), m.group(2)
                sections.setdefault(name, []).append((i, sec))
            for m in TOKEN_RE.finditer(text):
                tokens.setdefault(m.group(0), set()).add(i)
    return sections, tokens


def load_names(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return {r["name"] for r in data if isinstance(r, dict) and "name" in r}


def main():
    current_cmds = load_names(DATA_DIR / "at_commands.yaml")
    per = {}
    for ver, url in MANUALS.items():
        print("Processing " + ver + " ...", file=sys.stderr)
        p = download(ver, url)
        s, t = scan_pdf(p)
        per[ver] = {"sections": s, "tokens": t}
        print("  " + str(len(s)) + " sections, " + str(len(t)) + " tokens", file=sys.stderr)

    all_sections = set()
    all_tokens = set()
    for info in per.values():
        all_sections |= set(info["sections"])
        all_tokens |= set(info["tokens"])

    missing_sections = all_sections - current_cmds
    missing_tokens = all_tokens - current_cmds - missing_sections
    extra = current_cmds - all_tokens

    print()
    print("=" * 72)
    print("[A] In PDF section headers, missing from YAML: " + str(len(missing_sections)))
    print("=" * 72)
    for name in sorted(missing_sections):
        refs = []
        for ver, info in per.items():
            if name in info["sections"]:
                pageno, sec = info["sections"][name][0]
                refs.append(ver + " sec" + sec + " (p" + str(pageno) + ")")
        print("  " + name.ljust(22) + "  " + "; ".join(refs))

    print()
    print("=" * 72)
    print("[B] In PDF body only, missing from YAML: " + str(len(missing_tokens)))
    print("=" * 72)
    for name in sorted(missing_tokens):
        refs = []
        for ver, info in per.items():
            if name in info["tokens"]:
                pages = sorted(info["tokens"][name])[:3]
                refs.append(ver + " p" + str(pages))
        print("  " + name.ljust(22) + "  " + "; ".join(refs))

    print()
    print("=" * 72)
    print("[C] In YAML but no PDF token matched: " + str(len(extra)))
    print("=" * 72)
    for name in sorted(extra):
        print("  " + name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
