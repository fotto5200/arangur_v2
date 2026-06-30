# Briefing Spec Set Persistence Contract v1

Status: implemented optional backend skeleton.

## Purpose

Briefing spec set persistence stores draft Client Briefing Set and Advisor
Review Set specs created by the browser Report Element Finder / Composer. It is
the backend counterpart to the browser-local export shape defined in
`local_briefing_spec_set_contract_v1.md`.

This contract preserves local copy/download/restore as the default safe demo
handoff path. Backend save/load is optional, private-demo oriented, and does
not generate reports.

## Relationship To Local Export

The API accepts the same envelope emitted by the browser-local export:

- `schema_version`: `arangur.local_briefing_spec_set.v1`
- `synthetic_data`: `true`
- `client_context`
- ordered `client_briefing_set`
- ordered `advisor_review_set`

The original payload is stored as `raw_spec_set_json` in Postgres mode. Summary
fields and item rows are derived from that payload for listing and later private
demo workflows.

## API Behavior

`POST /api/briefing-spec-sets`

- Validates the local spec-set payload.
- In `DB_ENGINE=postgres` mode, saves a draft and returns its `spec_set_id`,
  counts, title, client context summary, and status.
- In `DB_ENGINE=none` mode, validates the payload and returns a clear
  not-configured response without saving.

`GET /api/briefing-spec-sets`

- Returns saved draft summaries in Postgres mode.
- Returns an empty list with a not-configured message in `DB_ENGINE=none` mode.

`GET /api/briefing-spec-sets/{spec_set_id}`

- Returns the saved summary, original payload, and derived item summaries in
  Postgres mode.
- Returns 404 when the spec set is not found or persistence is not configured.

`DELETE /api/briefing-spec-sets/{spec_set_id}`

- Deletes the saved draft in Postgres mode.
- Returns a calm no-op response in `DB_ENGINE=none` mode.

## `DB_ENGINE=none` Behavior

`DB_ENGINE=none` remains the default. App startup, ordinary tests, report
element catalog endpoints, workflow run endpoints, local export/restore, local
preview, and browser print/export do not require a database.

Save attempts in this mode return:

`Backend persistence is not configured. Use local export/download for now.`

No files, reports, or database records are created.

## `DB_ENGINE=postgres` Behavior

When `DB_ENGINE=postgres` and `DATABASE_URL` are configured, the existing schema
initialization path creates the briefing spec-set tables with
`CREATE TABLE IF NOT EXISTS`.

The schema is intentionally small and not a production migration system. Local
private-demo databases may need to be reset if this schema changes before a
future migration framework is adopted.

## Entity Sketch

`briefing_spec_set`

- `spec_set_id`
- `schema_version`
- `title`
- `client_name`
- `portfolio_context`
- `synthetic_data`
- `source`
- `status`
- `client_briefing_set_count`
- `advisor_review_set_count`
- `raw_spec_set_json`
- `summary_json`
- `created_at`
- `updated_at`

`briefing_spec_item`

- `item_id`
- `spec_set_id`
- `branch`: `client_briefing` or `advisor_review`
- `order_index`
- `element_id`
- `element_title`
- `placement`
- `advisor_internal_purpose`
- `parameters_json`
- `matched_view_id`
- `preview_available`
- `confidence_label`
- `raw_spec_json`

The item table is a summary/indexing layer. The raw browser payload remains the
source of truth for reconstructing the draft in the composer.

## Validation Rules

The API rejects payloads that:

- are not JSON objects;
- exceed the demo payload size limit;
- omit or mismatch `schema_version`;
- omit `synthetic_data` or set it to anything other than `true`;
- omit `client_context`;
- omit either ordered set list;
- include analytic items without `element_id` or `element_title`;
- include narrative items without a clear narrative type or title;
- include branch/target labels that conflict with the list they are in;
- include malformed parameter or matched-view objects;
- include obvious secret or real-data markers such as access tokens, API keys,
  private keys, SSNs, or routing-number labels.

## Deliberately Not Implemented

- Production authentication.
- Multi-user permissions or tenant isolation.
- Durable production client/account/holding modeling.
- Report generation from saved spec sets.
- Server-side preview/PDF generation.
- Deployment secrets.
- Alembic or a finalized migration system.
- Live Plaid, external APIs, real market data, or real client data.
