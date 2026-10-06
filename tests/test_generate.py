"""Idempotency test for tools/generate.py (pytest)."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATED_FILES = [
    PROJECT_ROOT / "include" / "sim800_at" / "at_types.hpp",
    PROJECT_ROOT / "include" / "sim800_at" / "at_commands.hpp",
    PROJECT_ROOT / "include" / "sim800_at" / "urcs.hpp",
    PROJECT_ROOT / "include" / "sim800_at" / "at_api.hpp",
]


def _hash_all():
    h = hashlib.sha256()
    for p in GENERATED_FILES:
        h.update(p.name.encode("utf-8"))
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def _run_generate():
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "tools" / "generate.py")],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"generate.py failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def test_generate_idempotent():
    """Running generate.py twice in a row must not change any generated file."""
    _run_generate()
    first = _hash_all()
    _run_generate()
    second = _hash_all()
    assert first == second, "generate.py is not idempotent"


def test_version_hpp_not_generated():
    """generate.py must not create or overwrite version.hpp."""
    version_path = PROJECT_ROOT / "include" / "sim800_at" / "version.hpp"
    before = version_path.read_bytes() if version_path.exists() else None
    _run_generate()
    after = version_path.read_bytes() if version_path.exists() else None
    assert before == after, "generate.py modified version.hpp"