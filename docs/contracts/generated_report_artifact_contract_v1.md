# Generated Report Artifact Contract v1

## Purpose

A generated report artifact is the first durable product object after an advisor-authored workflow is combined with a dated data snapshot. It is the object a later Presentation flow can open for client or advisor use.

This contract is intentionally small for the private demo. It defines the artifact shape and assembly behavior without creating a production report archive, report library, immutable audit system, or new UI surface.

## Relationship To Existing Objects

- Workflow: reusable advisor-authored report structure.
- Preview: temporary rendering of an in-progress workflow for review while editing.
- Generated report artifact: dated, data-populated output produced from a workflow and data snapshot.
- Presentation: opening a generated report artifact for client or advisor use.

The current implementation can assemble deterministic demo artifacts from existing briefing-set preview fixtures and can populate a browser-local saved workflow through `POST /api/generated-reports/demo-populate`. The API returns the artifact JSON directly and does not persist it.

## Demo Populate API

`POST /api/generated-reports/demo-populate` accepts the browser-local workflow/spec-set payload shape plus:

- `workflow_id`, optional
- `workflow_display_name`
- `report_type`: `client_briefing` or `advisor_review`
- `data_snapshot_label`, optional; defaults to `Current synthetic demo snapshot`
- `data_as_of`, optional; defaults to `2026-06-30`

The endpoint validates the local workflow payload, uses only committed synthetic demo rendered views, maps unsupported or unrenderable sections to clean placeholders, and returns a `generated_report_artifact.v1` object. It does not require Postgres, create report history, write artifact files, add report-library records, call external APIs, or use real client or market data.

## Artifact Fields

- `schema_version`: `generated_report_artifact.v1`.
- `builder_version`: deterministic builder identifier.
- `report_id`: stable artifact id for the demo output.
- `report_type`: `client_briefing` or `advisor_review`.
- `source_workflow_id`: nullable; may be absent for current local/demo artifacts.
- `source_workflow_display_name`: human-readable workflow name.
- `source_preview_id`: source preview id when assembled from a preview fixture.
- `report_title`: display title for the generated artifact.
- `generated_at`: deterministic generation timestamp for fixture/demo output.
- `data_as_of`: dated data snapshot value.
- `data_snapshot_label`: human-readable data snapshot label.
- `synthetic_data`: must be `true` for demo artifacts.
- `app_environment` / `runtime_mode`: optional runtime framing for private-demo output.
- `ordered_sections`: ordered section records.
- `unsupported_sections`: compact list of sections rendered as placeholders or unsupported.
- `caveats`: artifact-level caveats.
- `render_status`: `complete`, `partial`, or `demo_partial`.
- `text_content`: complete text rendering.
- `html_content`: complete HTML rendering.
- `metadata_json`: compact structured metadata useful to later product flows.
- `summary`: compact summary for tests and later APIs.

## Section Model

Each section includes:

- `section_id`
- `title`
- `section_type`: `narrative`, `report_element`, `unsupported`, or `caveat`
- `order_index`
- `html`
- `text`
- `source_element_id`, nullable
- `source_element_title`, nullable
- `status`: `rendered`, `placeholder`, `omitted`, or `unsupported`

Unsupported demo sections must use advisor-safe placeholder language such as `This section is not available in the demo generated report.` They must not expose stack traces, file paths, raw exceptions, or debugging instructions.

## Render Status

- `complete`: every requested section is rendered for the selected snapshot.
- `partial`: at least one section was omitted or rendered as a placeholder.
- `demo_partial`: deterministic private-demo artifact assembled from synthetic fixtures; suitable for product-path modeling, not production use.

The initial implementation uses `demo_partial` for demo artifacts because it proves the generated artifact object without claiming full report-generation coverage.

## Synthetic Demo Caveats

Generated report artifacts in this repo currently use synthetic/demo data only. They do not use real client data, live market data, live Plaid, external APIs, real credentials, or production deployment infrastructure.

## Deliberately Not Implemented

- Production report history.
- Report library UI.
- Durable generated report persistence.
- Present/view generated report library.
- Live data snapshots.
- Auth or permissions.
- Immutable audit archive.
- PDF generation.
- Database schema changes.
- Docker, Lightsail, Caddy, Cloudflare, or public deployment changes.

## UI Principle

Generated report artifacts are a product object, not a reason to expose debugging panels in the advisor path. The advisor UI should stay sparse: no new top-level home choices, no duplicate buttons, no generated-report dashboard, and no technical artifact inspection panels unless a later batch explicitly designs a small product-facing surface.
