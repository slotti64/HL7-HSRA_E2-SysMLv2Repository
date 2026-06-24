# Demo E2E — Opus come agente consumatore della knowledge base

Questa è la validazione end-to-end dell'Incremento 1: Claude Opus, via il server MCP `cc-sysml`,
consuma la knowledge base read-only e produce risposte **citabili** (ogni risultato porta la
coordinata `project/commit/element`).

## Prerequisiti
1. Stack C1+C3 attivo: `docker compose -f deploy/docker-compose.yml up -d --build` (vedi `deploy/README.md`).
2. Client API installato e `cc-sysml` con `SYSML_API_BASE_URL` impostata (vedi `docs/mcp-config.md`).
3. Libreria caricata: `python scripts/load_library.py` (annotare project id / commit / tag stampati).

## Flusso e prompt di esempio

### 1. Connettività
> Prompt: «Verifica che il repository SysML v2 sia raggiungibile.»

Atteso: Opus chiama `tool_repo_status` → `{"available": true, "base_url": "http://localhost:9000", ...}`.

### 2. Scoperta dei progetti
> Prompt: «Quali progetti (librerie) sono disponibili nel repository?»

Atteso: `tool_repo_list_projects` → elenco contenente **"HL7-HSRA Pattern Library"** con il suo id.
Opus riporta l'id come parte della citazione.

### 3. Navigazione versione
> Prompt: «Mostrami i commit di quella libreria e dimmi su quale coordinata immutabile citare.»

Atteso: `tool_repo_list_commits` → il commit creato dal load; Opus indica `project + commit` (o il tag
`hl7-hsra-patterns-v1`) come coordinata di citazione (spec §4.1).

### 4. Browsing dei pattern
> Prompt: «Elenca le definizioni di pattern presenti a quel commit.»

Atteso: `tool_repo_list_elements(project, commit)` → i Package
(`HL7HSRAServiceInteraction`, `HL7HSRAConsent`, `HL7HSRACapability`) e le loro definizioni
(`ServiceInteractionPattern`, `ConsentRequiredPattern`, `CapabilityPattern`, ...).

### 5. Query strutturata deterministica
> Prompt: «Trova tutte le PartDefinition nella libreria, alla versione citata.»

Atteso: `tool_repo_run_query(project, query_json, commit_id)` con questo body **verificato**
(attenzione: `value` deve essere un array JSON):

```json
{"@type": "Query",
 "where": {"@type": "PrimitiveConstraint", "inverse": false,
           "operator": "=", "property": "@type", "value": ["PartDefinition"]}}
```

Risultato deterministico e version-pinned (spec §4.2): le 7 PartDefinition della libreria.

### 6. Risoluzione di un elemento + citazione
> Prompt: «Dammi i dettagli del pattern ServiceInteractionPattern e cita la fonte.»

Atteso: `tool_repo_get_element(project, commit, element)` → dettagli dell'elemento; Opus chiude con
una citazione del tipo `project=<id>, commit=<id>, element=<id>`.

### 7. (Opzionale) Validazione di testo candidato
> Prompt: «È valido questo frammento SysML v2? `part def X { part y : X; }`»

Atteso: Opus usa `tool_syside_validate` (C6) per il parsing spec-compliant.

## Criterio di successo
- Ogni risposta a contenuto della KB include una coordinata `project/commit(/element)` verificabile.
- Le query strutturate restituiscono lo stesso risultato su commit fissato (riproducibilità).
- Nessun percorso di scrittura è disponibile all'agente (read-only by design, spec §4.3).

## Stato attuale — verificato live (pilot `2026-04`)
La catena completa è stata eseguita end-to-end contro lo stack Docker:

- `GET /projects` → `200 []` (smoke test); poi libreria caricata via `scripts/load_library.py`.
- Coordinate della libreria caricata (esempio di run):
  - project `5586b1c9-c010-474e-b13a-73dd028e0e4d`
  - commit `409196ae-79d0-499b-93fa-07eea859683e`
  - tag `hl7-hsra-patterns-v1`
- 21 elementi al commit (3 Package + 9 definizioni). `list_commits`, `run_query` e `get_element`
  del bridge restituiscono dati con coordinata commit completa.
- `pytest -m integration` verde (incluso il test live).

Quando lo stack è spento i tool `tool_repo_*` restituiscono un errore strutturato (`ok=false`) con
istruzioni, senza sollevare eccezioni — comportamento coperto dai test in
`CC_SysML/tests/integration/test_repo_integration.py`.

> Nota: i tool MCP funzionano out-of-the-box perché il bridge usa `requests` (già presente) e il
> base URL di default è `http://localhost:9000`. `SYSML_API_BASE_URL` serve solo per puntare altrove.
