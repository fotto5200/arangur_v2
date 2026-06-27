# Decision 0002: Copy Education Private Demo Stack

## Status

Accepted for the first Arangur v2 deployable demo design.

## Date

2026-06-27

## Decision

Arangur v2 will copy the Education private-demo deployment pattern for the first deployable demo:

- FastAPI backend served by `uvicorn`.
- Simple browser UI served by the backend/container.
- Dockerfile and Docker Compose.
- App service plus internal Postgres service.
- `.env.private-demo` pattern with committed example only.
- `APP_ENV=private_demo`.
- `PUBLIC_ORIGIN` and `ALLOWED_ORIGINS`.
- `DEMO_ADMIN_TOKEN` for protected admin/report surfaces.
- `CSRF_SECRET` if needed by the browser interaction model.
- `DATABASE_URL` pointing to the internal Compose `postgres` service.
- `/api/health`.
- Protected admin/report endpoints.
- Demo seed command that exercises real app/service paths.
- Lightsail Ubuntu VM.
- Caddy reverse proxy.
- Cloudflare DNS.

## Reason

The Education app already has a working private-demo deployment pattern. Reusing that shape reduces deployment design risk, keeps Arangur focused on its portfolio/reporting product loop, and avoids unnecessary early AWS complexity.

The current Arangur local demo already has a clean pipeline boundary. A FastAPI app can wrap those modules, persist run metadata in Postgres, and expose a small browser UI without changing analytics behavior.

## Consequences

Positive consequences:

- Faster path to a private browser demo.
- Familiar deployment model for Frank and future Codex batches.
- Clear split between local pipeline, app shell, persistence, and deployment.
- Avoids premature ECS/RDS or multi-service cloud architecture.
- Keeps Postgres internal to Docker networking for the first private demo.

Tradeoffs:

- The first deployment is private-demo grade, not production-grade.
- Demo admin token protection is not a production identity system.
- App/container filesystem artifact storage may need later replacement.
- The first database model will store run metadata and artifact pointers before full portfolio relational modeling.

## What Is Copied

- FastAPI plus `uvicorn` runtime.
- Backend-served browser UI.
- Docker Compose app plus Postgres.
- Private-demo env file pattern.
- Health endpoint convention.
- Protected admin/report surface pattern.
- Demo seed/preflight concept.
- Lightsail host plus Caddy reverse proxy.
- Cloudflare DNS in front of the host.

## What Is Not Copied

- Education domain models.
- Education UI or product flows.
- Education-specific seed data.
- Any credentials, secrets, or `.env` values.
- Production claims or compliance posture.
- A requirement to use AWS managed RDS, ECS, or other managed services for the first private demo.

## Open Questions

- What public/private demo subdomain should be used?
- Should the first browser UI use token-only API calls or cookie-backed sessions with CSRF protection?
- Should generated report artifacts live in a Docker volume initially, or inside an app-managed artifact directory mounted from the host?
- Which workflow runs should the seed command create by default beyond quarterly, data coverage, and Plaid-shaped intake?
- When should `scenario_result` become a first-class Postgres table versus remaining an artifact summary?
