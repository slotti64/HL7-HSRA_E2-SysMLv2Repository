# HL7 HSRA E2 SysML v2 Repository

The system's purpose is to implement a SysML v2 model repository that exposes standard APIs, natively manages model versioning, and makes the repository accessible to GenAI agents via the Model Context Protocol (MCP). 

The final goal is a curated knowledge base of reusable specification models (from HL7-HSRA) that humans and AI agents can query, reason over, and extend under governance.

### Design Principles (under revision)

 - Standards first. The repository conforms to the OMG SysML v2 Systems Modeling API and Services specification; bespoke behavior is confined to layers above the standard API.
 - Versioning is intrinsic. The native Project–Commit–Branch–Tag model of the standard is the single source of truth for history; no parallel versioning scheme is introduced.
 - Agents are clients, not privileged actors. Agent access is mediated by the MCP layer and is subject to the same authorization and governance as any other client.
 - Reproducibility. Every knowledge-base assertion resolves to an immutable coordinate (project, commit, element), ensuring deterministic, citable retrieval.
 - Separation of structure and semantics. Deterministic structural queries and approximate semantic retrieval are distinct paths that reconcile on stable element identifiers.

### Increment 1 — Read-only knowledge base (implemented)

Following the specification (`ProjectDocs/sysmlv2_mcp_spec_2.docx`, §5.2/§7.7), the first increment
delivers a **read-only** knowledge base, validated end-to-end against the OMG pilot:

- **C1 + C3** — the OMG `SysML-v2-API-Services` pilot (tag `2026-04`) on PostgreSQL, deployed via
  Docker (`deploy/`). Smoke test `GET /projects` → `200 []`.
- **C5** — the existing [`cc-sysml`](https://github.com/gitvendis/CC_SysML) MCP server, extended with
  read-only, **commit-pinned** repository tools (`tool_repo_*`) that talk to the pilot's REST API.
  Every result carries an immutable `project/commit/element` coordinate, so answers are citable.
- **C6** — curated HL7-HSRA specification patterns as parametric SysML v2 definitions
  (`models/patterns/`), validated with the spec-compliant SysIDE parser and loaded as a tagged,
  versioned library (`scripts/load_library.py`).
- **C2** — thin read-only posture for the PoC (`docs/security-notes.md`).

Out of scope for Increment 1 (deferred to Increment 2): semantic retrieval (C4), write/proposal and
governance (C7), full authorization, and observability — plus diagram generation.

**Documentation:** [`docs/repo-structure.md`](docs/repo-structure.md) ·
[`deploy/README.md`](deploy/README.md) · [`docs/mcp-config.md`](docs/mcp-config.md) ·
[`docs/versions.md`](docs/versions.md) · [`docs/demo-prompts.md`](docs/demo-prompts.md) ·
[`docs/security-notes.md`](docs/security-notes.md)

#### Quick start

```bash
# 1. Deploy C1 + C3 (see deploy/README.md for the one-time source clone)
docker compose -f deploy/docker-compose.yml up -d --build
curl http://localhost:9000/projects                 # -> 200 []

# 2. Validate and load the curated patterns
python scripts/validate_patterns.py                  # -> PASS (no real errors)
python scripts/load_library.py                       # creates project + commit + tag

# 3. Consume via the cc-sysml MCP tools (tool_repo_*) — see docs/demo-prompts.md
```
