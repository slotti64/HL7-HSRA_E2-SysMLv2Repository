# Configurazione MCP — iniezione di `SYSML_API_BASE_URL`

I nuovi tool `tool_repo_*` (Fase 3) leggono l'URL del repository SysML v2 dalla variabile
d'ambiente **`SYSML_API_BASE_URL`** (default `http://localhost:9000`, vedi `CC_SysML/src/cc_sysml/config.py`).

Il server `cc-sysml` è attualmente registrato a livello **globale** in `~/.claude/.claude.json`
con `env: {}`. Per attivare i tool di repository, aggiungere la variabile in **uno** dei due modi.

## Opzione A — `.mcp.json` di progetto (consigliata, self-contained)
Creare `.mcp.json` nella radice di questo repository con:

```json
{
  "mcpServers": {
    "cc-sysml": {
      "type": "stdio",
      "command": "C:\\Users\\slotti\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": ["-m", "cc_sysml.mcp_server"],
      "env": {
        "SYSML_API_BASE_URL": "http://localhost:9000"
      }
    }
  }
}
```

## Opzione B — registrazione globale
Aggiungere `"SYSML_API_BASE_URL": "http://localhost:9000"` dentro `mcpServers.cc-sysml.env`
in `~/.claude/.claude.json`.

> Nota: questi file sono caricati dal harness all'avvio; vanno modificati manualmente dall'utente
> (la modifica automatica è bloccata per sicurezza). Dopo la modifica, riavviare la sessione MCP.
