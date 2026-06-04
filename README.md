# HL7-HSRA_E2-SysMLv2Repository

The system's purpose is to implement a SysML v2 model repository that exposes standard APIs, natively manages model versioning, and makes the repository accessible to GenAI agents via the Model Context Protocol (MCP). 

The final goal is a curated knowledge base of reusable specification models (from HL7-HSRA) that humans and AI agents can query, reason over, and extend under governance.

**Design Principles** (under revision)

•	Standards first. The repository conforms to the OMG SysML v2 Systems Modeling API and Services specification; bespoke behavior is confined to layers above the standard API.
•	Versioning is intrinsic. The native Project–Commit–Branch–Tag model of the standard is the single source of truth for history; no parallel versioning scheme is introduced.
•	Agents are clients, not privileged actors. Agent access is mediated by the MCP layer and is subject to the same authorization and governance as any other client.
•	Reproducibility. Every knowledge-base assertion resolves to an immutable coordinate (project, commit, element), ensuring deterministic, citable retrieval.
•	Separation of structure and semantics. Deterministic structural queries and approximate semantic retrieval are distinct paths that reconcile on stable element identifiers.

_**The project is currently in an early design phase**_.
