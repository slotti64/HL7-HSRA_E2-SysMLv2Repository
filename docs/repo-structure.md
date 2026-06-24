# Struttura del repository (Incremento 1)

```
HL7-HSRA_E2-SysMLv2Repository/
├── README.md                  # Overview e principi di design
├── .mcp.json                  # Registrazione MCP cc-sysml di progetto (inietta SYSML_API_BASE_URL)
├── deploy/                    # C1 + C3: deploy del pilot SysML v2 API + PostgreSQL via Docker
│   ├── docker-compose.yml
│   ├── Dockerfile.sysml-api
│   └── README.md
├── models/
│   └── patterns/             # C6: libreria curata di pattern HL7-HSRA (.sysml)
├── scripts/
│   └── load_library.py       # Carica i pattern come Project + Commit + Tag nel repository
├── tests/
│   └── integration/          # Test E2E della catena tool MCP → API → DB
├── docs/
│   ├── versions.md           # Pinning delle versioni
│   ├── repo-structure.md     # Questo file
│   ├── security-notes.md     # Postura C2 (thin read-only) per il PoC
│   └── demo-prompts.md       # Prompt di consumo E2E per Opus
└── ProjectDocs/
    └── sysmlv2_mcp_spec_2.docx
```

I deliverable di **codice MCP** (bridge e tool `tool_repo_*`) vivono nel repo separato
`CC_SysML` (`src/cc_sysml/`), riusato ed esteso secondo il piano.
```
