# Deploy C1 + C3 — SysML v2 API & Services + PostgreSQL (Docker)

Questo stack ospita in locale il pilot OMG **SysML v2 API & Services** (C1, server REST con commit
graph) su **PostgreSQL** (C3). Il pilot è trattato come *black box* dietro l'API standard: si
**deploya e configura**, non si forka (spec §7.1).

## Prerequisiti
- Docker Desktop (con Docker Compose v2).
- Connessione di rete per il primo build (sbt scarica le dipendenze).

## Passi

1. **Clonare il sorgente upstream** dentro `deploy/` (la cartella è git-ignorata):
   ```bash
   git clone https://github.com/Systems-Modeling/SysML-v2-API-Services.git \
       deploy/SysML-v2-API-Services
   ```
   > Bloccare la versione: eseguire `git checkout <tag>` nel clone e annotare il tag in
   > `docs/versions.md` (vedi rischio "version drift", spec §7.5).

2. **Copiare il Dockerfile** nel sorgente clonato (il build context è quella cartella):
   ```bash
   cp deploy/Dockerfile.sysml-api deploy/SysML-v2-API-Services/Dockerfile
   ```

3. **Avviare lo stack**:
   ```bash
   docker compose -f deploy/docker-compose.yml up -d --build
   ```
   Il primo build è lento (compilazione sbt + download dipendenze). L'API ascolta su `:9000`,
   PostgreSQL su `:5432`.

## Smoke test
```bash
curl http://localhost:9000/projects          # atteso: 200 con [] (catalogo vuoto)
# Documentazione API: http://localhost:9000/docs/
```

## Note di configurazione
- Il pilot ha la connessione JDBC **hardcoded** in `conf/META-INF/persistence.xml`
  (`jdbc:postgresql://localhost:5432/sysml2`, utente `postgres`, password `mysecretpassword`).
  Il `Dockerfile.sysml-api` riscrive **solo l'host** (`localhost` → `postgres`, il nome del servizio
  compose) via `sed` al build: è un override di deployment, non una modifica del codice.
- Credenziali di default lasciate come da pilot (PoC locale). Per ambienti non locali vanno
  cambiate (DB password) e protette dietro il gateway C2 (vedi `docs/security-notes.md`).

## Stop / reset
```bash
docker compose -f deploy/docker-compose.yml down            # stop
docker compose -f deploy/docker-compose.yml down -v         # stop + cancella il volume DB
```
