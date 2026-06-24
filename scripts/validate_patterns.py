#!/usr/bin/env python3
"""Validate the curated HL7-HSRA pattern library with syside-cli (C6).

Runs the spec-compliant Langium parser (syside-cli, the same engine Eclipse
SysON uses, bundled with CC_SysML) over each ``models/patterns/*.sysml`` file
and classifies its diagnostics into:

  * REAL errors  — syntax errors ("Expecting ..."), unresolved user-defined
    references, or "A Feature must be typed by at least one type". Genuine defects.
  * SYSTEMIC notices — "implicit specialization" against the Kernel/Systems
    standard library (Base::*, Parts::*, Actions::*, Items::*). The single-file
    syside-cli bundled with CC_SysML does NOT ship the standard library, so every
    definition reports these regardless of correctness. They are resolved by the
    deployed SysML v2 API & Services (C1), which loads the full library.

syside-cli writes diagnostics to STDERR (the build log goes to stdout and the
JSON AST is suppressed when any diagnostic exists), so this script reads STDERR
directly rather than going through CC_SysML's SysideBridge.

Exit code is non-zero only if a REAL error is found — safe as a pre-load gate.

Usage:
    python scripts/validate_patterns.py
    SYSIDE_CLI_PATH=/path/to/syside-cli.js python scripts/validate_patterns.py
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

_DIAG_RE = re.compile(r"^line\s+(\d+):\s+(.*)$")
_SYSTEMIC_MARKERS = (
    "implicit specialization",
    "implicit definition specialization",
    "implicit usage specialization",
)

_DEFAULT_CLI = Path(r"C:/Users/slotti/Documents/GitHub/CC_SysML/resources/bin/syside-cli.js")
PATTERNS_DIR = Path(__file__).resolve().parent.parent / "models" / "patterns"


def find_cli() -> Path | None:
    env = os.environ.get("SYSIDE_CLI_PATH")
    if env and Path(env).is_file():
        return Path(env)
    if _DEFAULT_CLI.is_file():
        return _DEFAULT_CLI
    return None


def is_systemic(message: str) -> bool:
    return any(m in message for m in _SYSTEMIC_MARKERS)


def validate_file(node: str, cli: Path, path: Path) -> tuple[list[str], int]:
    """Return (real_error_lines, systemic_count) for one .sysml file."""
    proc = subprocess.run(
        [node, str(cli), "dump", str(path), "--validate"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    real: list[str] = []
    systemic = 0
    for line in proc.stderr.splitlines():
        m = _DIAG_RE.match(line.strip())
        if not m:
            continue
        msg = m.group(2)
        if is_systemic(msg):
            systemic += 1
        else:
            real.append(f"line {m.group(1)}: {msg}")
    return real, systemic


def main() -> int:
    node = shutil.which("node")
    if not node:
        print("ERROR: Node.js not found on PATH.")
        return 2
    cli = find_cli()
    if not cli:
        print("ERROR: syside-cli.js not found. Set SYSIDE_CLI_PATH.")
        return 2

    files = sorted(PATTERNS_DIR.glob("*.sysml"))
    if not files:
        print(f"No .sysml files found in {PATTERNS_DIR}")
        return 2

    total_real = 0
    for f in files:
        real, systemic = validate_file(node, cli, f)
        status = "OK" if not real else "REAL ERRORS"
        print(f"\n{f.name}: {status}  (real={len(real)}, systemic/stdlib={systemic})")
        for line in real:
            print(f"  REAL  {line}")
        total_real += len(real)

    print("\n" + "=" * 64)
    if total_real == 0:
        print("PASS: no real errors. Remaining notices are stdlib-implicit "
              "(resolved by the deployed repository at load time).")
        return 0
    print(f"FAIL: {total_real} real error(s) found.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
