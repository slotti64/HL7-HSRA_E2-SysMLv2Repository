# Versioni bloccate (pinning)

La specifica (§7.5) identifica il *version drift* come rischio: SysML v2, la sua API e il pilot OMG
sono recenti e in evoluzione. Per garantire build riproducibili, l'Incremento 1 blocca le versioni
dei componenti riusati. **Non aggiornare a metà build.**

| Componente | Versione bloccata | Note |
|------------|-------------------|------|
| `syside-cli` (SysIDE/Langium) | `0.9.0` | Già integrato in CC_SysML; parser primario spec-compliant (vedi `tool_bridge_status`). |
| `Systems-Modeling/SysML-v2-API-Services` (C1) | tag `2026-04` | Server REST + commit graph. Deploy via Docker, non build/fork. |
| `requests` (transport del bridge) | `>=2.28` | Il bridge `sysml_api_bridge` parla REST/JSON direttamente via `requests` (extra `repo` di CC_SysML), anziché il client OpenAPI generato. Verificato end-to-end contro il pilot `2026-04`. |
| `postgres` (C3) | tag immagine maggiore fissato (es. `postgres:16`) | Store durable; volume persistente. |
| `pysysml2` | `6dfaf83` | Validatore secondario opzionale (già pinnato in CC_SysML `pyproject.toml`). |

## Come aggiornare il pin del client/server
1. Annotare qui il commit/tag scelto.
2. Allineare l'extra `repo` in `CC_SysML/pyproject.toml`.
3. Ri-eseguire la verifica end-to-end (vedi piano, sezione "Verifica end-to-end").
