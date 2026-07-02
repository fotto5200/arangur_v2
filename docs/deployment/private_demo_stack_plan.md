# Private Demo Stack Plan

## Purpose

Arangur v2 should copy the Education private-demo deployment pattern for its first deployable demo instead of inventing a separate stack. The goal is a small, understandable private deployment that can run on a Lightsail Ubuntu VM behind Caddy and Cloudflare, while still using only synthetic/mock Arangur data.

This started as a design plan. The local Docker/private-demo implementation now lives in `Dockerfile`, `docker-compose.yml`, `.env.private-demo.example`, and `docs/deployment/private_demo_docker.md`. Lightsail, Caddy, Cloudflare, DNS, and production hardening remain future work.

Frank verified the local Docker runtime smoke on 2026-07-02: the app and internal Postgres service came up with Compose, `/api/health` returned `status: ok`, health confirmed `app_env: private_demo`, `runtime_mode: private_demo`, `db_engine: postgres`, and `database_configured: true`, `/app/` loaded, and a Postgres-backed briefing spec-set POST/list smoke worked. This verification is local/private-demo only; it does not complete public deployment, production authentication, generated report history, real-client-data readiness, or Caddy/Lightsail/Cloudflare setup.

## Stack To Copy

Use:

- Python FastAPI backend served by `uvicorn`.
- Simple browser UI served by the backend/container.
- `Dockerfile`.
- `docker-compose.yml`.
- `docker-compose.private-demo.example.yml`.
- App service plus Postgres service.
- Internal Postgres service on the Docker network.
- `.env.private-demo.example`.
- `APP_ENV=private_demo`.
- `PUBLIC_ORIGIN` and `ALLOWED_ORIGINS`.
- `DEMO_ADMIN_TOKEN` for protected admin/report surfaces.
- `CSRF_SECRET` if browser form/session protections need it.
- `DATABASE_URL` pointing to the Docker Compose `postgres` service.
- `/api/health` health endpoint.
- Protected admin/report endpoints.
- Demo seed command that exercises the real app/service paths.
- Lightsail Ubuntu VM.
- Caddy reverse proxy.
- Cloudflare DNS.

Avoid for the first private demo:

- AWS managed RDS.
- ECS.
- Kubernetes.
- Separate frontend hosting.
- Live Plaid.
- Real client data.
- External market-data APIs.

## Proposed Compose Services

### `app`

Purpose:

- Run the FastAPI app via `uvicorn`.
- Serve API endpoints and simple browser UI.
- Generate synthetic demo workflow/report artifacts.
- Read/write run metadata through Postgres.

Expected internal port:

- `8000` inside the container.

Expected inputs:

- Environment variables from `.env.private-demo`.
- Mounted or image-contained synthetic fixtures.
- Local artifact output directory.

### `postgres`

Purpose:

- Store private-demo run metadata, artifact records, summaries, and audit events.

Network:

- Internal Docker Compose network only.
- Not exposed publicly.
- Not accessed directly from Caddy or Cloudflare.

Persistence:

- Docker named volume for Postgres data.

## Implemented Local Files

The local Docker/private-demo implementation added:

- `Dockerfile`
- `docker-compose.yml`
- `.env.private-demo.example`
- app settings support for `APP_ENV=private_demo`, `DB_ENGINE=postgres`, and `DATABASE_URL`
- local smoke documentation in `docs/deployment/private_demo_docker.md`

Future deployment or preflight batches may still add host-specific Compose overlays, seed/preflight commands, or deployment docs after product and ops decisions are explicit.

Do not commit:

- `.env.private-demo`
- passwords
- tokens
- private keys
- Cloudflare credentials
- real client data

## Environment Variables

Required first private-demo variables:

| Variable | Example | Purpose |
| --- | --- | --- |
| `APP_ENV` | `private_demo` | Runtime mode gate. |
| `PUBLIC_ORIGIN` | `https://arangur-demo.example.com` | Canonical browser origin for links/cookies. |
| `ALLOWED_ORIGINS` | `https://arangur-demo.example.com` | CORS/browser origin allowlist. |
| `DEMO_ADMIN_TOKEN` | not committed | Token for protected admin/report endpoints. |
| `CSRF_SECRET` | not committed | Optional CSRF/session secret if browser forms need it. |
| `DB_ENGINE` | `postgres` | Persistence engine selection. |
| `POSTGRES_DB` | `arangur_private_demo` | Compose Postgres database name. |
| `POSTGRES_USER` | `arangur_demo` | Compose Postgres user. |
| `POSTGRES_PASSWORD` | not committed | Compose Postgres password. |
| `DATABASE_URL` | `postgresql://arangur_demo:...@postgres:5432/arangur_private_demo` | App connection string to internal Postgres service. |

`DATABASE_URL` should point at `postgres`, the Compose service name, not a public host.

## Health Checks

Required health endpoint:

- `GET /api/health`

Suggested response shape:

- `status`: `ok`
- `app_env`: `private_demo`
- `database`: `ok` or `unavailable`
- `version` or build identifier if available

Health checks should verify basic application readiness and optionally database connectivity. They should not reveal secrets, environment values, or internal stack details beyond what is needed for smoke tests.

## Protected Admin And Report Endpoints

The first demo should protect:

- Run workflow endpoint.
- Run history and run detail APIs.
- Report artifact APIs.
- Admin seed/preflight endpoints.
- Browser pages that expose report artifacts.

Minimum first protection:

- `DEMO_ADMIN_TOKEN` accepted through an `Authorization` header or equivalent private-demo access mechanism.
- No token in URLs.
- No committed token.
- Clear caveat that this is private-demo protection, not production identity and access management.

If the browser UI submits forms or mutating requests with cookies, include `CSRF_SECRET` and CSRF protections. If the first browser UI uses token-authenticated API calls without cookies, CSRF may be deferred, but the env slot should be reserved.

## Demo Seed Command

The seed command should exercise real app/service paths.

Recommended behavior:

1. Confirm `APP_ENV=private_demo`.
2. Confirm database connectivity.
3. Run the same service used by the workflow-run API.
4. Generate deterministic runs:
   - `native_demo` + `quarterly_review`.
   - `native_demo` + `data_coverage_review`.
   - `plaid_mock` + `intake_review`.
5. Persist workflow runs and report artifact records.
6. Print run IDs and report URLs.

The seed command must not:

- Insert fake rows that bypass app logic.
- Use real Plaid.
- Use external APIs.
- Read secrets beyond normal app settings.
- Require real client data.

## Local Smoke-Test Commands

The verified local smoke path uses Windows cmd commands from the repo root:

```cmd
copy .env.private-demo.example .env.private-demo
docker compose --env-file .env.private-demo up --build
```

Then verify:

```cmd
curl.exe http://127.0.0.1:8000/api/health
start "" http://127.0.0.1:8000/app/
curl.exe -X POST http://127.0.0.1:8000/api/briefing-spec-sets -H "Content-Type: application/json" -d "{\"schema_version\":\"arangur.local_briefing_spec_set.v1\",\"synthetic_data\":true,\"client_context\":{\"client_family\":\"Northstar Family Office\",\"portfolio_context\":\"Demo portfolio\"},\"client_briefing_set\":[],\"advisor_review_set\":[]}"
curl.exe http://127.0.0.1:8000/api/briefing-spec-sets
docker compose --env-file .env.private-demo down
```

If Docker Desktop is not running its Linux engine, start Docker Desktop and wait for the engine before retrying. If port `8000` is already in use, stop the conflicting local process or use a temporary host-side port mapping and matching URL for smoke checks. To reset the local Postgres demo volume, run `docker compose --env-file .env.private-demo down -v`. Do not commit `.env.private-demo`.

For the Lightsail host through Caddy:

```bash
curl https://<private-demo-host>/api/health
```

Protected endpoint smoke tests should pass the demo admin token through a header and must avoid printing the token in logs.

## Lightsail Host Shape

Recommended first host:

- One Lightsail Ubuntu VM.
- Docker and Docker Compose plugin installed.
- Repo checkout or release artifact deployed to the host.
- `.env.private-demo` created manually on host and not committed.
- Caddy installed on the host as reverse proxy.
- Cloudflare DNS points the demo subdomain to the Lightsail public IP.

No actual public subdomain is chosen in this plan. Choosing the subdomain is a product/ops decision for a later batch.

## Caddy Reverse Proxy

Caddy should:

- Terminate HTTPS.
- Proxy private-demo traffic to the app container port on localhost.
- Preserve host/proto headers.
- Enforce sane request size limits if file upload is ever added.
- Avoid exposing Postgres.

The first deployable app should not rely on Caddy for application authorization. Caddy is the edge proxy; the app still protects report/admin surfaces.

## Cloudflare DNS

Cloudflare should:

- Host DNS for the chosen demo subdomain.
- Point the subdomain at the Lightsail public IP.
- Avoid coupling Arangur to AWS managed services for the first private demo.

Cloudflare account credentials, API tokens, and zone details must not be committed.

## Artifact Storage

For the first private demo, generated report artifacts can remain on the app container filesystem or a mounted volume. Postgres should store artifact metadata and paths.

Future concerns:

- Backup and retention.
- Cleaning old artifacts.
- Separating generated artifacts from static assets.
- Moving artifacts to object storage only when the deployment needs it.

## What Not To Claim About Production Security

The private-demo stack should not claim:

- Production-grade authentication.
- Multi-tenant authorization.
- Compliance readiness.
- Audited data retention.
- Disaster recovery.
- Enterprise secrets management.
- Production database operations.

Correct framing:

- The stack is a private demo deployment.
- It protects admin/report surfaces with a demo token.
- It keeps Postgres internal to Docker networking.
- It uses synthetic/mock data only.
- It is suitable for a private product walkthrough, not production client use.

## First Implementation Batches

Recommended sequence:

1. FastAPI app shell and `/api/health`.
2. Settings and private-demo protection helpers.
3. Workflow-run API wrapping existing pipeline modules.
4. Postgres persistence skeleton.
5. Browser UI shell.
6. Docker Compose private-demo stack.
7. Seed/preflight script.
8. Lightsail/Caddy/Cloudflare deployment guide.
