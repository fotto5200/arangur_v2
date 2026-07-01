# Local Private-Demo Docker Stack

## Purpose

This stack runs the Arangur v2 FastAPI demo app and an internal Postgres container for local/private-demo smoke testing. It is not a public deployment recipe, does not configure Caddy, Cloudflare, DNS, or Lightsail, and must not be used with real client data or real secrets.

## Files

- `Dockerfile` builds the FastAPI app image from the repo and serves `arangur.app.main:app` with `uvicorn` on `0.0.0.0:8000`.
- `docker-compose.yml` defines the `app` and internal `postgres` services plus a named Postgres data volume.
- `.env.private-demo.example` provides demo-only local values for Compose. Copy it before running the stack; do not commit a real `.env.private-demo`.

## Start The Stack

Use Windows cmd-friendly commands from the repo root:

```cmd
copy .env.private-demo.example .env.private-demo
docker compose --env-file .env.private-demo up --build
```

Then check:

```cmd
curl.exe http://127.0.0.1:8000/api/health
```

Open:

- `http://127.0.0.1:8000/app/`
- `http://127.0.0.1:8000/api/briefing-spec-sets`

## Stop Or Reset

```cmd
docker compose --env-file .env.private-demo down
```

To remove the local Postgres demo volume:

```cmd
docker compose --env-file .env.private-demo down -v
```

## Postgres Behavior

Compose sets `DB_ENGINE=postgres` and points `DATABASE_URL` at the internal `postgres` service. On app startup, the existing safe schema initialization path runs `CREATE TABLE IF NOT EXISTS` for workflow-run tables and briefing spec-set tables. The default non-Docker local path remains `DB_ENGINE=none` and does not require Docker or Postgres.

The browser Developer / QA backend save/load controls exercise `/api/briefing-spec-sets` against Postgres when the stack is running. A simple API-level save/list check is:

```cmd
curl.exe -X POST http://127.0.0.1:8000/api/briefing-spec-sets -H "Content-Type: application/json" -d "{\"schema_version\":\"arangur.local_briefing_spec_set.v1\",\"synthetic_data\":true,\"client_context\":{\"client_family\":\"Northstar Family Office\",\"portfolio_context\":\"Demo portfolio\"},\"client_briefing_set\":[],\"advisor_review_set\":[]}"
curl.exe http://127.0.0.1:8000/api/briefing-spec-sets
```

## Boundaries

- Local/private-demo only.
- Synthetic/mock data only.
- No production authentication claims.
- No live Plaid, live market data, external APIs, DNS, Caddy, Cloudflare, or Lightsail setup.
- Do not put real secrets in `.env.private-demo`.
