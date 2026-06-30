# Briefing Set Preview Contract v1

Status: implemented synthetic baseline.

This contract defines the first file-based composition layer for rendered report
element views. It sits between:

```text
report-element view JSON plus Markdown/HTML fragments
-> simple Client Briefing Set and Advisor Review Set previews
-> later browser preview or spec-set integration
```

The preview layer is deterministic and standard-library-only. It does not
modify the browser composer, add FastAPI routes, persist briefing sets, generate
charts, or create production client-ready reports.

## Source Inputs

The preview builder consumes rendered report-element views under:

- `data/simulation/report_element_views/`

Those views are produced by `src/arangur/report_elements/rendering.py` and are
governed by `docs/contracts/report_element_rendering_contract_v1.md`.

## Output Files

The default writer emits:

- `data/simulation/briefing_set_previews/client_briefing_set_preview.json`
- `data/simulation/briefing_set_previews/client_briefing_set_preview.md`
- `data/simulation/briefing_set_previews/client_briefing_set_preview.html`
- `data/simulation/briefing_set_previews/advisor_review_set_preview.json`
- `data/simulation/briefing_set_previews/advisor_review_set_preview.md`
- `data/simulation/briefing_set_previews/advisor_review_set_preview.html`
- `data/simulation/briefing_set_previews/briefing_set_preview_index.json`
- `data/simulation/briefing_set_previews/index.html`

The index links to the two preview files and to the rendered element view
summary.

## Preview Payload Shape

Each preview uses `schema_version: briefing_set_preview.v1` and includes:

- `preview_id`
- `preview_type`: `client_briefing_set` or `advisor_review_set`
- `title`
- `purpose`
- `client_or_portfolio_context`
- `preview_summary`
- `ordered_elements`
- `included_element_ids`
- `advisor_notes`
- `review_notes`
- `caveats`
- `confidence_summary`
- `source_view_summary`
- `synthetic_data: true`
- `validation`

Each ordered element includes:

- `order`
- `element_key`
- `element_id`
- `element_title`
- `placement`
- `element_view_path`
- `markdown_fragment_path`
- `html_fragment_path`
- `headline`
- `summary_text`
- `key_metrics`
- `confidence_summary`
- `caveats`
- `human_review_count`
- `human_review_items`
- `as_of_date`
- `synthetic_data: true`

Path fields are structured JSON metadata. Markdown and HTML preview bodies must
not foreground JSON paths, repo mechanics, report package links, or debug
artifacts.

## Default Client Preview

The default Client Briefing Set preview includes:

1. Portfolio Status
2. Concentration by Theme
3. Scenario Impact by Manager - AI/chip selloff
4. Data Confidence Note

The tone is client-facing and answer-first. It uses concrete values from the
rendered element views, keeps caveats concise, includes a synthetic/demo notice,
and treats scenario output as a deterministic risk prompt, not a forecast.

## Default Advisor Preview

The default Advisor Review Set preview includes:

1. Manager Comparison
2. Cash Generation Summary
3. Concentration by Sector/Industry
4. Scenario Impact by Manager - AI/chip selloff
5. Data Confidence Note

The tone is advisor/internal. It emphasizes diagnostics, manager review, cash
and liquidity review, scenario review, data confidence, and human-review items.

## Markdown And HTML Behavior

Markdown previews are simple readable documents with title, context, ordered
elements, key metrics, confidence, review notes, and caveats.

HTML previews are static semantic documents using ordinary HTML elements. They
do not include JavaScript, CSS frameworks, charts, browser composer state, or
external assets.

`index.html` is a simple static file that links to the client preview, advisor
preview, Markdown files, JSON payloads, and rendered element view summary.

## Validation Invariants

`validate_briefing_set_preview(...)` checks that:

- required preview identity, type, title, purpose, context, elements, caveats,
  confidence, and synthetic-data fields are present;
- ordered elements are sequential;
- ordered elements reference existing rendered element view, Markdown, and HTML
  files;
- client previews include at least three elements;
- advisor previews include at least four elements;
- advisor previews include data-confidence and human-review language;
- Markdown and HTML previews are non-empty when supplied;
- preview bodies avoid raw internal artifact clutter such as JSON paths, `/api/`
  routes, report package links, and debug artifact references;
- preview text avoids production-accuracy, guarantee, and real-data markers.

Validation returns structured `status`, `errors`, `warnings`,
`builder_version`, and `validated_at` fields.

## Public Functions

The preview builder is implemented in
`src/arangur/report_elements/briefing_set_preview.py`:

- `load_report_element_views(view_dir)`
- `build_default_client_briefing_set_preview(view_payloads)`
- `build_default_advisor_review_set_preview(view_payloads)`
- `render_briefing_set_preview_markdown(preview_payload)`
- `render_briefing_set_preview_html(preview_payload)`
- `write_demo_briefing_set_previews(...)`
- `validate_briefing_set_preview(preview_payload)`

It can run from the repo root:

```powershell
python src\arangur\report_elements\briefing_set_preview.py
```

## Deliberately Not Implemented Yet

This preview layer does not implement:

- browser UI integration;
- saved or persisted briefing sets;
- FastAPI preview routes;
- full client-ready report generation;
- charts or charting dependencies;
- production valuation, accounting, or performance claims;
- backend persistence;
- Docker/Postgres changes;
- live Plaid, vendor market data, external APIs, or real client data.
