# Local Private-Demo Docker Stack

## Purpose

This stack runs the Arangur v2 FastAPI demo app and an internal Postgres container for local/private-demo smoke testing. It is not a public deployment recipe, does not configure Caddy, Cloudflare, DNS, or Lightsail, and must not be used with real client data or real secrets.

## Verified Runtime Smoke

Frank verified the local Docker runtime smoke on 2026-07-02:

- The FastAPI app container and internal Postgres container came up locally with `docker compose --env-file .env.private-demo up --build`.
- `GET /api/health` returned `status: ok`.
- Health reported `app_env: private_demo`, `runtime_mode: private_demo`, `db_engine: postgres`, and `database_configured: true`.
- `http://127.0.0.1:8000/app/` loaded.
- A Postgres-backed briefing spec-set POST/list smoke worked through `/api/briefing-spec-sets`.

This verifies local/private-demo runtime readiness only. It does not mean public deployment is complete, production authentication exists, real client data is allowed, generated report history exists, or Caddy, Lightsail, Cloudflare, DNS, and production hardening are configured.

## Files

- `Dockerfile` builds the FastAPI app image from the repo and serves `arangur.app.main:app` with `uvicorn` on `0.0.0.0:8000`.
- `docker-compose.yml` defines the `app` and internal `postgres` services plus a named Postgres data volume.
- `.env.private-demo.example` provides demo-only local values for Compose. Copy it before running the stack; do not commit a real `.env.private-demo`.

## Local Preflight Flow

Start the stack with Windows cmd commands from the repo root:

```cmd
copy .env.private-demo.example .env.private-demo
docker compose --env-file .env.private-demo up --build
```

In another cmd, run the smoke script:

```cmd
scripts\private_demo_smoke.cmd
```

The smoke script expects the stack to already be running. It uses `curl.exe` only and checks:

- `GET http://127.0.0.1:8000/api/health`
- `GET http://127.0.0.1:8000/app/`
- `GET http://127.0.0.1:8000/api/report-elements`
- `POST http://127.0.0.1:8000/api/briefing-spec-sets`
- `GET http://127.0.0.1:8000/api/briefing-spec-sets`

The POST uses `scripts\fixtures\private_demo_seed_briefing_spec_set.json`, a synthetic/demo-only payload with one Client Briefing Set item and one Advisor Review Set item. The smoke script does not require `jq` or any non-standard command-line tools.

Open the app:

```cmd
start "" http://127.0.0.1:8000/app/
```

Stop the stack:

```cmd
docker compose --env-file .env.private-demo down
```

Or use:

```cmd
scripts\private_demo_down.cmd
```

If Docker reports that the daemon or Linux engine is unavailable, start Docker Desktop, confirm the Linux engine is running, and rerun the `docker compose` command. If `8000` is already occupied by another local app, stop that app before starting this stack or temporarily adjust the host-side Compose port and use the matching URL for smoke checks. If a curl smoke check fails, confirm the stack is still running and inspect app logs:

```cmd
docker compose --env-file .env.private-demo logs app
```

## Stop Or Reset

```cmd
docker compose --env-file .env.private-demo down
```

To remove the local Postgres demo volume:

```cmd
scripts\private_demo_down.cmd --reset
```

The reset helper asks for confirmation before running `docker compose --env-file .env.private-demo down -v`. That command deletes the local private-demo Postgres volume and all saved demo metadata in it. Use it only when you want a fresh local database.

## Postgres Behavior

Compose sets `DB_ENGINE=postgres` and points `DATABASE_URL` at the internal `postgres` service. On app startup, the existing safe schema initialization path runs `CREATE TABLE IF NOT EXISTS` for workflow-run tables and briefing spec-set tables. The default non-Docker local path remains `DB_ENGINE=none` and does not require Docker or Postgres.

The browser Developer / QA backend save/load controls exercise `/api/briefing-spec-sets` against Postgres when the stack is running. The checked-in smoke script performs an API-level save/list check with the synthetic seed payload:

```cmd
scripts\private_demo_smoke.cmd
```

The underlying POST can be run directly if needed:

```cmd
curl.exe -X POST http://127.0.0.1:8000/api/briefing-spec-sets -H "Content-Type: application/json" --data-binary "@scripts\fixtures\private_demo_seed_briefing_spec_set.json"
curl.exe http://127.0.0.1:8000/api/briefing-spec-sets
```

## Boundaries

- Local/private-demo only.
- Synthetic/mock data only.
- The smoke seed payload is demo metadata only, not generated report history.
- No production authentication claims.
- No generated report history yet.
- No live Plaid, live market data, external APIs, DNS, Caddy, Cloudflare, or Lightsail setup.
- Do not put real secrets in `.env.private-demo`.
- Do not commit `.env.private-demo`.
