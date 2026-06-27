# Persistence Model Plan

## Purpose

The first deployable Arangur demo needs enough Postgres persistence to track workflow runs, report artifacts, and summary metadata. It should not turn the first private demo into a full production portfolio database.

The current JSON artifacts remain the canonical evidence for detailed outputs. Postgres should initially store durable run history, search/list metadata, artifact references, and selected summaries needed by the browser UI.

Current implementation baseline: `src/arangur/app/persistence.py` defines optional Postgres persistence for `workflow_run`, `report_artifact`, and `run_event`. The default `DB_ENGINE=none` mode remains file-backed and requires no database. When `DB_ENGINE=postgres` and `DATABASE_URL` are set, the app can initialize the minimal tables and persist run metadata after local report generation.

This is still not a full migration system or production data model.

## Design Principles

- Store run metadata before modeling every portfolio detail.
- Keep synthetic/mock boundaries explicit.
- Preserve links to generated JSON, Markdown, and HTML artifacts.
- Prefer JSONB for complete generated payload snapshots only when useful.
- Avoid real client data assumptions.
- Keep the first schema small enough for private-demo operation.

## Entity Summary

| Entity | Purpose |
| --- | --- |
| `demo_actor` | Represents a private-demo user or system actor. |
| `portfolio_source` | Records which synthetic/mock source adapter produced a run. |
| `portfolio_snapshot` | Records a canonical snapshot artifact and summary metadata. |
| `workflow_run` | Central run record for one source/workflow execution. |
| `report_artifact` | Links generated reports and JSON artifacts to a workflow run. |
| `scenario_result` | Stores scenario-result artifact metadata and summary values. |
| `data_coverage_result` | Stores data coverage artifact metadata and confidence summary. |
| `run_event` | Optional audit/event trail for private-demo operations. |

## `demo_actor`

### Purpose

Represents the actor that initiated a private-demo workflow run. This can be a human demo user, an admin token identity, or a seed process.

### Key Fields

- `id`
- `actor_key`
- `display_name`
- `actor_type`: `admin`, `seed`, `system`, or `demo_user`
- `created_at`
- `last_seen_at`

### Relationship To Current Outputs

Current JSON outputs do not have user identity. This table adds private-demo operational context without modifying report artifacts.

### Stores

- Summary metadata only.

### First-Demo Simplifications

- One default admin/seed actor is enough.
- No password store.
- No production identity provider.

### Future Production Concerns

- Real authentication.
- Role-based authorization.
- Audit retention.
- User deletion and data governance.

## `portfolio_source`

### Purpose

Records the source adapter used to generate a workflow run.

### Key Fields

- `id`
- `source_name`: `native_demo` or `plaid_mock`
- `source_adapter`: `demo_json` or `plaid_mock`
- `source_label`
- `source_kind`: `synthetic_fixture` or `plaid_shaped_mock`
- `is_synthetic`
- `source_files` as JSONB or text array
- `created_at`

### Relationship To Current Outputs

Maps to `source_name`, `source_adapter`, and source metadata in `canonical_portfolio_snapshot.json` and `report_package.json`.

### Stores

- Source summary metadata.
- Optional list of fixture file paths.

### First-Demo Simplifications

- Only two source records are needed.
- No live source credentials.
- No external sync status.

### Future Production Concerns

- Plaid item provenance.
- Custodian source credentials and secrets policy.
- Source licensing and access controls.
- Reconciliation status.

## `portfolio_snapshot`

### Purpose

Records a generated canonical snapshot artifact and small summary fields for browsing and joins.

### Key Fields

- `id`
- `snapshot_id`
- `portfolio_id`
- `portfolio_name`
- `source_id`
- `valuation_date`
- `reporting_currency`
- `account_count`
- `holding_count`
- `cash_balance_count`
- `security_count`
- `artifact_path`
- `payload_json` optional JSONB
- `created_at`

### Relationship To Current Outputs

Links to `canonical_portfolio_snapshot.json`.

### Stores

- Artifact path and summary metadata.
- Optional normalized snapshot JSONB if the app needs database retrieval without reading the artifact file.

### First-Demo Simplifications

- Store artifact path and summary fields first.
- Avoid decomposing accounts, holdings, securities, and cash into relational tables.

### Future Production Concerns

- Snapshot versioning.
- Field-level provenance.
- Reconciliation status.
- Retention and deletion.
- Support for real client data only after an authorized production design.

## `workflow_run`

### Purpose

Central record for one requested execution of an Arangur demo workflow.

### Key Fields

- `id`
- `run_id`
- `source_id`
- `snapshot_id`
- `actor_id`
- `workflow_type`
- `workflow_label`
- `status`: `queued`, `running`, `succeeded`, `failed`
- `app_env`
- `valuation_date`
- `started_at`
- `finished_at`
- `error_code`
- `error_message`
- `portfolio_market_value`
- `portfolio_cash_value`
- `data_confidence_label`
- `human_review_item_count`
- `created_at`
- `updated_at`

### Relationship To Current Outputs

Maps directly to `run_metadata` and `data_coverage_result` summaries in `report_package.json`.

### Stores

- Summary metadata.
- Status and timing.
- Links to source, snapshot, artifacts, scenario results, and data coverage result.

### First-Demo Simplifications

- Synchronous execution is acceptable.
- No distributed job queue.
- No multi-tenant isolation.

### Future Production Concerns

- Background jobs.
- Idempotency.
- Concurrent runs.
- Retry handling.
- Tenant and user authorization.
- Operational observability.

## `report_artifact`

### Purpose

Records generated artifacts for a workflow run.

### Key Fields

- `id`
- `workflow_run_id`
- `artifact_type`: `canonical_snapshot`, `valuation_result`, `exposure_overlap_result`, `scenario_result`, `data_coverage_result`, `report_package`, `markdown_report`, `html_report`
- `format`: `json`, `markdown`, `html`
- `path`
- `display_label`
- `content_hash` optional
- `size_bytes` optional
- `created_at`

### Relationship To Current Outputs

Represents files currently written under `reports/demo/` and workflow-specific output folders.

### Stores

- Artifact path and metadata.
- Not raw file contents for the first demo.

### First-Demo Simplifications

- Local filesystem paths are enough.
- No object storage.
- No signed URL system.

### Future Production Concerns

- Artifact retention.
- Access-controlled download URLs.
- Hash verification.
- Object storage migration.
- Redaction for real data.

## `scenario_result`

### Purpose

Stores summary metadata for generated deterministic scenario outputs.

### Key Fields

- `id`
- `workflow_run_id`
- `scenario_id`
- `scenario_name`
- `valuation_date`
- `portfolio_before_value`
- `portfolio_after_value`
- `portfolio_impact_value`
- `portfolio_impact_percent`
- `artifact_path`
- `payload_json` optional JSONB
- `created_at`

### Relationship To Current Outputs

Links to `scenario_result.json`, which may contain a set of scenario results. The first model can either store one row per scenario in the result set or one row for the primary scenario and rely on artifact JSON for the rest.

### Stores

- Scenario summary metadata and artifact path.
- Optional JSONB payload.

### First-Demo Simplifications

- Store primary scenario summary first.
- Keep full details in the JSON artifact.

### Future Production Concerns

- Scenario library/source versioning.
- Key-driver assumptions.
- Stochastic simulation metadata.
- Model provenance and caveats.

## `data_coverage_result`

### Purpose

Stores summary metadata for generated data coverage and valuation confidence output.

### Key Fields

- `id`
- `workflow_run_id`
- `overall_confidence`
- `identifier_coverage`
- `price_coverage`
- `classification_coverage`
- `source_transparency`
- `valuation_method_confidence`
- `scenario_mapping_confidence`
- `human_review_item_count`
- `data_quality_flag_count`
- `artifact_path`
- `payload_json` optional JSONB
- `created_at`

### Relationship To Current Outputs

Links to `data_coverage_result.json` and the `data_coverage_result` summary inside `report_package.json`.

### Stores

- Confidence summary metadata.
- Human-review count.
- Artifact path.
- Optional full JSONB result.

### First-Demo Simplifications

- Store summary values for fast run-list display.
- Keep detailed security/holding/account coverage in artifact JSON.

### Future Production Concerns

- Human-review workflow/task status.
- Reconciliation metrics.
- Source inventory linkage.
- Stale-price and licensing flags.
- Production data-quality policies.

## `run_event`

### Purpose

Optional audit/event trail for private-demo operations.

### Key Fields

- `id`
- `workflow_run_id` nullable
- `actor_id` nullable
- `event_type`: `run_requested`, `run_started`, `artifact_written`, `run_succeeded`, `run_failed`, `seed_started`, `seed_finished`
- `message`
- `metadata_json` optional JSONB
- `created_at`

### Relationship To Current Outputs

Current JSON outputs do not include operational events. This table supports private-demo debugging and seed verification.

### Stores

- Event metadata and messages.

### First-Demo Simplifications

- Keep event messages minimal.
- Do not store secrets or request headers.

### Future Production Concerns

- Structured audit logging.
- Retention policy.
- Security event review.
- Redaction.

## First-Demo Relationship Sketch

```text
demo_actor 1 -> many workflow_run
portfolio_source 1 -> many portfolio_snapshot
portfolio_source 1 -> many workflow_run
portfolio_snapshot 1 -> many workflow_run
workflow_run 1 -> many report_artifact
workflow_run 1 -> many scenario_result
workflow_run 1 -> 1 data_coverage_result
workflow_run 1 -> many run_event
```

## First Migration Scope When Authorized

The first implementation migration should include:

- `demo_actor`
- `portfolio_source`
- `portfolio_snapshot`
- `workflow_run`
- `report_artifact`
- `data_coverage_result`
- optional `run_event`

`scenario_result` can be included if the browser UI needs scenario summaries in run lists; otherwise it can wait until the scenario source model is designed.

## What Not To Persist Yet

Do not persist as first-class tables yet:

- Individual holdings.
- Tax lots.
- Transactions.
- Real account identifiers.
- Uploaded documents.
- Plaid tokens or item credentials.
- External market-data records.
- Legacy MATLAB-derived outputs.

Those require separate authorization and production data-governance design.
