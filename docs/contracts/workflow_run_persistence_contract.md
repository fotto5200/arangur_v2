# Workflow Run Persistence Contract

## Purpose

This contract describes the first persistence skeleton for Arangur v2 private-demo workflow runs. It stores synthetic run metadata and report artifact references only. Detailed analytics outputs remain in generated JSON artifacts under `reports/demo/`.

## Modes

`DB_ENGINE=none` is the default local mode. The app does not open a database connection, does not initialize tables, and continues to list runs by scanning `reports/demo/**/report_package.json`.

`DB_ENGINE=postgres` with `DATABASE_URL` enables optional Postgres persistence. The app initializes minimal tables if missing and records run metadata after the existing file-backed pipeline generates report artifacts.

## Tables

`workflow_run` stores one row per workflow execution:

- `run_id`
- `source`
- `source_adapter`
- `workflow_type`
- `workflow_display_name`
- `status`
- `synthetic_data`
- `output_dir`
- `generated_at`
- `valuation_date`
- `data_confidence_label`
- `data_confidence_summary`
- `human_review_item_count`
- `report_package_path`
- `report_package_url`

`report_artifact` stores artifact references for a run:

- `run_id`
- `artifact_type`
- `label`
- `path`
- `url`

`run_event` stores a minimal event trail:

- `run_id`
- `event_type`
- `message`
- `details_json`

## Boundaries

The persistence layer must not store Plaid tokens, credentials, real client data, account identifiers from real institutions, private documents, or legacy MATLAB outputs.

The first skeleton does not decompose holdings, tax lots, transactions, securities, accounts, or managers into production tables. Those remain future data-model decisions and require separate authorization.

## API Relationship

`POST /api/runs` always runs the existing local pipeline first. In Postgres mode, the resulting run summary and artifact records are then persisted.

`GET /api/runs` and `GET /api/runs/{run_id}` work in file-backed mode without a database. In Postgres mode they can return persisted run summaries; if no persisted rows exist yet, file-backed report-package scanning remains available.
