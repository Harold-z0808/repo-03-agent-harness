"""
check_env.py - Week 3 environment self-check.
Run from the project root:
    uv run python check_env.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

OK = "OK"
FAIL = "FAIL"
fail_count = 0


def check(passed: bool, name: str, detail: str = "") -> None:
    """Print one check result."""

    global fail_count
    mark = OK if passed else FAIL
    print(f"{mark} {name}" + (f" - {detail}" if detail else ""))
    if not passed:
        fail_count += 1


def display_path(path: str) -> str:
    """Display a path relative to cwd when possible."""

    try:
        cwd = Path.cwd().resolve()
        relative = Path(path).resolve().relative_to(cwd)
        return str(Path(cwd.name) / relative)
    except ValueError:
        return path


load_dotenv()

major, minor = sys.version_info[:2]
ver = f"{major}.{minor}.{sys.version_info.micro}"
check((major, minor) in {(3, 11), (3, 12)}, "Python version", ver)

uv_path = shutil.which("uv") or str(Path.home() / ".local" / "bin" / "uv")
if uv_path and Path(uv_path).exists():
    try:
        out = subprocess.check_output([uv_path, "--version"], text=True).strip()
        check(True, "uv", out)
    except Exception as exc:
        check(False, "uv", f"found but failed: {exc}")
else:
    check(False, "uv", "not installed")

in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
check(
    in_venv,
    "virtual environment",
    display_path(sys.prefix) if in_venv else "use uv run python check_env.py",
)

openai_key = os.getenv("OPENAI_API_KEY")
check(bool(openai_key), "OPENAI_API_KEY", "detected" if openai_key else "required for class demos")

base_url = os.getenv("OPENAI_BASE_URL")
if base_url is not None:
    parsed = urlparse(base_url)
    valid_base_url = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    check(valid_base_url, "OPENAI_BASE_URL", base_url if valid_base_url else "must be full URL")

print("\n" + "=" * 40)
if fail_count == 0:
    print("Environment check passed.")
else:
    print(f"{fail_count} check(s) failed.")
    sys.exit(1)

