# Deployable Demo App Architecture

## Purpose

The first deployable Arangur demo app should make the existing synthetic workflow/report loop usable from a browser in a private demo environment. It should let a reviewer choose a synthetic source, choose an advisor workflow, run the existing analysis path, browse prior runs, and inspect reports plus data coverage confidence summaries.

This app is not a production client portal. It is a deployable wrapper around the current local demo pipeline so Arangur can be shown privately on a small VM without inventing a separate stack.

## Local Pipeline Versus Deployable App

The current local pipeline is a command-line and file-output workflow:

```text
data/demo fixtures -> canonical snapshot -> valuation -> exposure/overlap -> scenario -> data coverage -> report package
```

The deployable app should wrap that same product loop:

```text
browser UI -> FastAPI workflow-run endpoint -> existing pipeline/service modules -> persisted run metadata -> report browser
```

The local pipeline remains useful for deterministic development and artifact regeneration. The deployable app adds:

- A browser control surface.
- Run history.
- Protected report/admin surfaces.
- Persistent metadata and artifact pointers.
- Health checks and private-demo deployment conventions.

## Proposed Runtime Shape

```text
Browser UI
  -> FastAPI backend served by uvicorn
  -> Arangur pipeline/service modules
  -> Postgres run metadata
  -> generated report artifacts
```

The backend should serve both the simple browser UI and JSON API from the same container for the first private demo. A separate frontend build system is not needed until the UI scope grows.

## Proposed FastAPI Backend Structure

Future implementation can add an application package under `src/arangur/` or a small app entrypoint, but this design batch does not implement it.

Suggested backend responsibilities:

- Load app settings from environment variables.
- Serve `GET /api/health`.
- Serve static browser assets or server-rendered HTML for the demo UI.
- Expose protected workflow-run and report APIs.
- Validate source/workflow choices against existing supported values.
- Call existing pipeline functions instead of duplicating analytics.
- Persist workflow-run metadata and artifact references.
- Return summary payloads for run history and report browser pages.

Suggested internal modules when implementation is authorized:

- `app_settings`: environment parsing and private-demo settings.
- `app_main`: FastAPI application factory.
- `routes_health`: health and readiness endpoints.
- `routes_demo`: run workflow, run history, report metadata, artifact retrieval.
- `auth_demo`: demo admin token checks and optional CSRF helpers.
- `persistence`: Postgres connection/session and repository functions.
- `artifact_store`: local artifact path policy and report file lookup.
- `workflow_service`: wrapper around existing pipeline modules.

## Proposed Browser UI Structure

The first browser UI should be a utilitarian private-demo control panel, not a marketing site or production dashboard.

Required first UI controls:

- Source selector: `native_demo` / `plaid_mock`.
- Workflow selector: `quarterly_review` / `manager_overlap_review` / `scenario_risk_review` / `intake_review` / `data_coverage_review`.
- Run workflow button.
- Run history/list.
- Report viewer/link panel.
- Data coverage/confidence summary.
- Synthetic-data caveat.

Recommended first pages:

- `/`: demo run console with selectors and latest run summary.
- `/runs`: run history with filters by source and workflow.
- `/runs/{run_id}`: run detail with links to Markdown, HTML, JSON artifacts, and confidence summary.
- `/reports/{run_id}`: report viewer or redirect to generated HTML artifact.
- `/admin`: protected operational view for seed/preflight status, if needed.

The UI should keep caveats visible near run controls and reports:

- Synthetic data only.
- No live Plaid.
- No real client data.
- No external market data.
- Not investment advice.

## Proposed App Routes And Pages

| Route | Surface | Purpose | Protection |
| --- | --- | --- | --- |
| `/` | Browser page | Run console and latest run summary. | Demo access policy, likely protected for private demo. |
| `/runs` | Browser page | Browse workflow-run history. | Protected. |
| `/runs/{run_id}` | Browser page | Show run metadata, artifact links, confidence summary. | Protected. |
| `/reports/{run_id}` | Browser page | Render or link the generated HTML/Markdown report. | Protected. |
| `/admin` | Browser page | Seed/preflight/admin diagnostics if included. | Admin token required. |

## Proposed API Endpoints

| Endpoint | Method | Purpose | Notes |
| --- | --- | --- | --- |
| `/api/health` | `GET` | Health check for container/proxy smoke tests. | Unauthenticated or minimally exposed. |
| `/api/sources` | `GET` | Return available synthetic source adapters. | `native_demo`, `plaid_mock`. |
| `/api/workflows` | `GET` | Return available workflow types. | Mirrors local workflow templates. |
| `/api/workflow-runs` | `POST` | Start a workflow run. | Protected; validates source/workflow. |
| `/api/workflow-runs` | `GET` | List recent workflow runs. | Protected. |
| `/api/workflow-runs/{run_id}` | `GET` | Return run metadata and artifact summary. | Protected. |
| `/api/workflow-runs/{run_id}/artifacts` | `GET` | List artifact records. | Protected. |
| `/api/reports/{run_id}/html` | `GET` | Return generated HTML report or signed/internal link. | Protected. |
| `/api/reports/{run_id}/markdown` | `GET` | Return generated Markdown report. | Protected. |
| `/api/data-coverage/{run_id}` | `GET` | Return confidence summary or full result. | Protected. |
| `/api/admin/seed-demo` | `POST` | Run deterministic demo seed path. | Admin token required. |

For the first private demo, `POST /api/workflow-runs` can run synchronously if execution is fast. A later version can add background jobs if runtime grows.

## Reusing Existing Pipeline Modules

The app should reuse the current implementation boundaries:

- Source loading and canonicalization from the native demo and Plaid-shaped mock adapters.
- Valuation, exposure/overlap, scenario, and data coverage modules.
- Workflow template validation.
- Markdown/HTML report generation.
- Report package generation and artifact naming policy.

The app should not reimplement analytics in route handlers. Route handlers should validate a request, call a workflow service, persist metadata, and return a run summary.

## What Should Remain Outside Runtime

The first deployable runtime should not include:

- Live Plaid Link, Plaid Sandbox, or Plaid production calls.
- External market-data APIs.
- Real client data, credentials, or statement uploads.
- Legacy MATLAB inspection or execution.
- Stochastic scenario simulation.
- Private asset valuation automation.
- Production account management or entitlement logic.
- Production-grade document ingestion.

Current restart docs, roadmaps, and generated local examples remain repo documentation, not runtime dependencies.

## Workflow Run Representation

A workflow run should represent one requested execution of:

```text
source_adapter + workflow_type + valuation_date + generated artifacts
```

Minimum run metadata:

- `run_id`.
- `source_name`.
- `source_adapter`.
- `workflow_type`.
- `workflow_label`.
- `status`: queued, running, succeeded, failed.
- `requested_by` or demo actor.
- `created_at`, `started_at`, `finished_at`.
- `valuation_date`.
- Artifact paths.
- Portfolio total and cash value.
- Data confidence label and human-review count.
- Error summary if failed.

The run should link to current JSON outputs rather than forcing every full JSON artifact into first-version database tables. Postgres can store summaries and artifact locations first, then add JSONB snapshots later if useful.

## Report Browsing

Report browsing should begin from persisted `workflow_run` records and linked `report_artifact` records.

First report browser behavior:

- Show run list sorted newest first.
- Show source/workflow labels.
- Show valuation date and generated time.
- Show report links: HTML, Markdown, package JSON, data coverage JSON.
- Show data confidence and human-review count.
- Keep synthetic-data caveats visible.
- Hide or protect raw artifact retrieval behind the demo admin/report protection policy.

The static `reports/demo/index.html` remains useful for local file review, but the deployable app should eventually produce a database-backed run index.

## Demo Data Seeding

The first seed path should exercise real app/service paths, not insert fake database rows that bypass the workflow.

Seed command behavior:

1. Start app with `APP_ENV=private_demo`.
2. Use the same service called by `POST /api/workflow-runs`.
3. Run a small deterministic set of source/workflow combinations:
   - `native_demo` + `quarterly_review`.
   - `native_demo` + `data_coverage_review`.
   - `plaid_mock` + `intake_review`.
4. Persist run metadata and artifact records.
5. Verify generated artifacts exist.

Seed data must remain synthetic/mock only.

## Synthetic And Mock Boundaries

The deployable demo may use:

- `data/demo/demo_portfolio.json`.
- `data/demo/market_data_fixture.json`.
- `data/demo/scenario_definitions.json`.
- `data/demo/plaid_mock_investments.json`.
- Generated synthetic report artifacts.

The deployable demo must not use:

- Real client data.
- Real Plaid access tokens or item IDs.
- External market data.
- Private documents or credentials.
- Any `.env` file committed to git.

## Non-Goals For The First Deployable App

- Production authentication or multi-tenant authorization.
- Real Plaid integration.
- Real custodian ingestion.
- External market-data ingestion.
- Production database migrations beyond a small first schema.
- Background worker infrastructure unless synchronous runs become too slow.
- Rich interactive charting.
- File upload.
- Real client data workflows.
- Production security claims.
- AWS managed RDS, ECS, or multi-service cloud architecture.

## Implementation Order

Recommended sequence:

1. FastAPI app shell and `/api/health`.
2. Protected demo admin/report access policy.
3. Workflow-run service wrapper around existing pipeline modules.
4. Postgres persistence skeleton for run metadata and artifacts.
5. Browser UI shell with selectors and run list.
6. Docker Compose private-demo local stack.
7. Demo seed/preflight script.
8. Lightsail/Caddy/Cloudflare deployment docs.
