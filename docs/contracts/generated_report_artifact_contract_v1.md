# Generated Report Artifact Contract v1

## Purpose

A generated report artifact is the first durable product object after an advisor-authored workflow is combined with a dated data snapshot. It is the object the private-demo Presentation flow can open for client or advisor use.

This contract is intentionally small for the private demo. It defines the artifact shape and assembly behavior without creating a production report archive, report library, immutable audit system, backend generated-report persistence, or full report-management UI.

## Relationship To Existing Objects

- Workflow: reusable advisor-authored report structure.
- Preview: temporary rendering of an in-progress workflow for review while editing.
- Generated report artifact: dated, data-populated output produced from a workflow and data snapshot.
- Presentation: opening a generated report artifact for client or advisor use.

The current implementation can assemble deterministic demo artifacts from existing briefing-set preview fixtures and can populate a browser-local saved workflow through `POST /api/generated-reports/demo-populate`. The API returns the artifact JSON directly and does not persist it to the backend.

## Demo Populate API

`POST /api/generated-reports/demo-populate` accepts the browser-local workflow/spec-set payload shape plus:

- `workflow_id`, optional
- `workflow_display_name`
- `report_type`: `client_briefing` or `advisor_review`
- `data_snapshot_label`, optional; defaults to `Current synthetic demo snapshot`
- `data_as_of`, optional; defaults to `2026-06-30`

The endpoint validates the local workflow payload, uses only committed synthetic demo rendered views, maps unsupported or unrenderable sections to clean placeholders, and returns a `generated_report_artifact.v1` object. For matched analytic sections, generated reports reuse rendered fragment detail comparable to Preview rather than substituting summary-only generated-report sections. It does not require Postgres, create report history, write artifact files, add report-library records, call external APIs, or use real client or market data.

## Browser-Local Presentation Shelf

The static private-demo UI stores successful Populate responses in browser `localStorage` under `arangur.local_generated_reports.v1`. Shelf records are keyed by artifact `report_id`, carry compact display metadata plus the full returned artifact payload, and are used by Present / view reports to list, open, and delete browser-local generated report artifacts. Shelf rows show the generated report title, source workflow name, local generated timestamp, and data snapshot label so repeated generated reports from the same source workflow remain distinguishable.

Deleting a shelf record removes only that browser-local generated report record. It does not delete or mutate the source saved workflow. This shelf is not backend persistence, production report history, a report library, an immutable archive, cross-browser sync, or a production records system.

## Demo Content Shape

Generated demo artifacts render the selected advisor-authored workflow body. They preserve the ordered workflow items, narrative section-title text, narrative body text, selected report-element titles, and matched rendered fragment detail available in Preview. Generated artifacts must not add framing, closing prompts, follow-up sections, or other narrative body sections that were not present in the saved workflow.

Report-level metadata remains separate from body sections. The artifact may carry title, source workflow, generated timestamp, data snapshot, data-as-of date, and a concise synthetic-demo caveat in top-level fields, header text, or footer text. That metadata is not represented as `ordered_sections`.

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
- `ordered_sections`: ordered advisor-authored workflow body section records.
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
- Backend durable generated report persistence.
- Full generated-report search, filter, version, or history UI.
- Live data snapshots.
- Auth or permissions.
- Immutable audit archive.
- PDF generation.
- Database schema changes.
- Docker, Lightsail, Caddy, Cloudflare, or public deployment changes.

## UI Principle

Generated report artifacts are a product object, not a reason to expose debugging panels in the advisor path. The advisor UI should stay sparse: no new top-level home choices, no duplicate buttons, no generated-report dashboard, and no technical artifact inspection panels. The current Present shelf is intentionally minimal and product-facing: it lists browser-local artifacts created by Populate and opens the selected artifact in a clean presentation view.
