# Note di sicurezza — Gateway C2 (Incremento 1, thin read-only)

L'Incremento 1 è una knowledge base **read-only**. La postura di sicurezza è volutamente minimale
e adeguata a un PoC locale; l'autorizzazione completa è differita all'Incremento 2 (spec §3.2).

## In scope (Incremento 1)
- **Solo lettura.** Gli unici percorsi esposti agli agenti sono i tool MCP `tool_repo_*`, tutti di
  lettura. Non esiste alcun tool di scrittura (`propose_change` è differito). Gli agenti **non**
  possono promuovere né committare.
- **Gateway sottile.** Davanti al pilot C1 si pone, se necessario, un reverse proxy che consente i
  soli verbi GET e l'endpoint di query, rifiutando POST/PUT/DELETE verso `/projects/**`. Per il PoC
  locale può anche essere assente: la sola superficie agente è read-only per costruzione.
- **Coordinate citabili, non dati sensibili negli identificatori.** I risultati portano coordinate
  `project/commit/element`; non inserire dati sensibili in id, query string o argomenti dei tool che
  finiscono nei log (spec §4.3).

## Fuori scope (rinviato all'Incremento 2)
- Classi di principal (human / tool / agent) e policy per progetto/branch/operazione.
- Autenticazione OIDC/token, rate limiting e quote (più severe per il traffico agente).
- Audit completo degli eventi di stato e provenance (C8).

## Credenziali del pilot
Il pilot usa credenziali DB di default (`postgres`/`mysecretpassword`) hardcoded; accettabili solo
in locale. Per qualunque ambiente condiviso: cambiare la password DB, non esporre la porta 9000
pubblicamente e mettere il gateway read-only davanti all'API.
