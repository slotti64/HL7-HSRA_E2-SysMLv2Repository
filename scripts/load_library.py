#!/usr/bin/env python3
"""Load the curated HL7-HSRA patterns into the SysML v2 repository as a tagged library.

This realises the C6 curation step of Increment 1: it creates a Project, commits a
projection of the ``models/patterns/*.sysml`` definitions, and applies a Tag so the
library is referenced by an **immutable coordinate** (project + commit/tag), never a
mutable branch head (spec §4.1).

Round-trip note (spec §6.2 risk): faithfully mapping full SysML v2 textual notation to
the API element graph is the known round-trip challenge. For the PoC this script loads
a **named projection** — each pattern Package and its top-level definitions (PartDefinition,
RequirementDefinition, ActionDefinition) with their declared names — which is enough to
make the library browsable and citable via the read tools. The ``.sysml`` files remain the
human-authored source of truth in the repository.

Usage:
    # Offline: parse patterns and print/save the commit payload (no API needed)
    python scripts/load_library.py --dry-run

    # Live: create project + commit + tag against the deployed repository
    python scripts/load_library.py
    SYSML_API_BASE_URL=http://localhost:9000 python scripts/load_library.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any

PATTERNS_DIR = Path(__file__).resolve().parent.parent / "models" / "patterns"
OUT_DIR = Path(__file__).resolve().parent / "out"

PROJECT_NAME = "HL7-HSRA Pattern Library"
TAG_NAME = "hl7-hsra-patterns-v1"

# Map SysML v2 textual keywords to API element @type.
_DEF_TYPE = {
    "part": "PartDefinition",
    "requirement": "RequirementDefinition",
    "action": "ActionDefinition",
}
_PACKAGE_RE = re.compile(r"\bpackage\s+([A-Za-z_]\w*)\s*\{")
_DEF_RE = re.compile(r"\b(part|requirement|action)\s+def\s+([A-Za-z_]\w*)")


def _new_id() -> str:
    return str(uuid.uuid4())


def parse_pattern(path: Path) -> dict[str, Any]:
    """Extract the package name and top-level reusable definitions from a .sysml file."""
    text = path.read_text(encoding="utf-8")
    pkg_match = _PACKAGE_RE.search(text)
    package = pkg_match.group(1) if pkg_match else path.stem
    defs = [
        {"keyword": kw, "name": name, "type": _DEF_TYPE[kw]}
        for kw, name in _DEF_RE.findall(text)
    ]
    return {"file": path.name, "package": package, "definitions": defs}


def build_change(patterns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build the Commit 'change' list (DataVersions) for the parsed patterns.

    For each package: a Package element owning one OwningMembership per definition,
    each membership owning the definition element. New elements use identity=null.
    """
    change: list[dict[str, Any]] = []

    def add(payload: dict[str, Any]) -> None:
        change.append({"@type": "DataVersion", "identity": None, "payload": payload})

    for pat in patterns:
        memberships: list[dict[str, str]] = []
        for d in pat["definitions"]:
            def_id = _new_id()
            mem_id = _new_id()
            add({"@id": def_id, "@type": d["type"], "declaredName": d["name"]})
            add({
                "@id": mem_id,
                "@type": "OwningMembership",
                "ownedRelatedElement": [{"@id": def_id}],
            })
            memberships.append({"@id": mem_id})
        pkg_id = _new_id()
        add({
            "@id": pkg_id,
            "@type": "Package",
            "declaredName": pat["package"],
            "ownedRelationship": memberships,
        })
    return change


def do_dry_run(patterns: list[dict[str, Any]], change: list[dict[str, Any]]) -> int:
    print(f"Parsed {len(patterns)} pattern file(s):")
    for p in patterns:
        names = ", ".join(f"{d['name']}({d['type']})" for d in p["definitions"])
        print(f"  - {p['file']}: package {p['package']} -> {names or '(no top-level defs)'}")
    commit_body = {"@type": "Commit", "change": change}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "commit_payload.json"
    out_path.write_text(json.dumps(commit_body, indent=2), encoding="utf-8")
    print(f"\nCommit payload: {len(change)} DataVersion(s) -> {out_path}")
    print("Dry run only: no API calls were made.")
    return 0


def _eid(obj: Any) -> Any:
    """Extract an element/resource id from a pilot JSON object (@id or id)."""
    if isinstance(obj, dict):
        return obj.get("@id") or obj.get("id")
    return None


def do_live(change: list[dict[str, Any]]) -> int:
    """Create project + commit + tag against the deployed pilot over plain HTTP.

    Uses ``requests`` directly against the SysML v2 API & Services REST endpoints
    (no generated client needed). The pilot accepts/returns JSON-LD style objects
    with ``@id``/``@type``.
    """
    import requests  # stdlib-adjacent, widely available

    base_url = os.environ.get("SYSML_API_BASE_URL", "http://localhost:9000").rstrip("/")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    print(f"Connecting to SysML v2 API at {base_url} ...")

    # 1. Create project (the pilot returns it with a default branch + initial commit).
    r = requests.post(
        f"{base_url}/projects",
        json={"@type": "Project", "name": PROJECT_NAME},
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    project_id = _eid(r.json())
    print(f"Created project '{PROJECT_NAME}' id={project_id}")

    # 2. Find the default branch to commit onto.
    r = requests.get(f"{base_url}/projects/{project_id}/branches", headers=headers, timeout=30)
    r.raise_for_status()
    branches = r.json() or []
    branch_id = _eid(branches[0]) if branches else None
    print(f"Default branch id={branch_id}")

    # 3. Commit the projection.
    commit_body = {"@type": "Commit", "change": change}
    url = f"{base_url}/projects/{project_id}/commits"
    if branch_id:
        url += f"?branchId={branch_id}"
    r = requests.post(url, json=commit_body, headers=headers, timeout=120)
    r.raise_for_status()
    commit_id = _eid(r.json())
    print(f"Created commit id={commit_id} ({len(change)} DataVersions)")

    # 4. Tag the commit as an immutable library reference (best-effort).
    try:
        r = requests.post(
            f"{base_url}/projects/{project_id}/tags",
            json={"@type": "Tag", "name": TAG_NAME, "taggedCommit": {"@id": commit_id}},
            headers=headers,
            timeout=30,
        )
        if r.ok:
            print(f"Tagged commit as '{TAG_NAME}': {_eid(r.json())}")
        else:
            print(f"WARNING: tag creation returned {r.status_code}. Cite the commit id instead.")
    except requests.RequestException as exc:
        print(f"WARNING: tag creation failed ({exc}). Cite the commit id instead.")

    print("\nLibrary loaded. Citable coordinate:")
    print(json.dumps({"project": project_id, "commit": commit_id, "tag": TAG_NAME}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Load HL7-HSRA patterns as a tagged library.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse patterns and emit the commit payload without calling the API.")
    args = parser.parse_args()

    files = sorted(PATTERNS_DIR.glob("*.sysml"))
    if not files:
        print(f"No .sysml files in {PATTERNS_DIR}")
        return 2
    patterns = [parse_pattern(f) for f in files]
    change = build_change(patterns)

    if args.dry_run:
        return do_dry_run(patterns, change)
    return do_live(change)


if __name__ == "__main__":
    raise SystemExit(main())
