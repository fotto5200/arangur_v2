# Report Element Rendering Contract v1

Status: implemented synthetic baseline.

This contract defines the first rendering bridge from report-element input
payloads into simple deterministic report-element views. It sits between:

```text
report-element input payloads
-> report-element view JSON plus Markdown/HTML fragments
-> later briefing set preview
```

The renderer does not generate full client briefings, briefing sets, charts,
browser UI state, database records, report packages, or production reports.

## Source Inputs

The renderer consumes only report-element input payloads under:

- `data/simulation/report_element_inputs/`

Those payloads are produced by
`src/arangur/report_elements/input_mapping.py` and are governed by
`docs/contracts/report_element_input_mapping_contract_v1.md`.

## Output Files

The default renderer writes to:

- `data/simulation/report_element_views/`

For each input payload, it writes:

- `<input_stem>.view.json`
- `<input_stem>.md`
- `<input_stem>.html`

It also writes:

- `report_element_view_summary.json`

The default committed fixture set renders:

- `portfolio_status`
- `concentration_theme`
- `concentration_sector_industry`
- `scenario_impact_by_manager_ai_chip_selloff`
- `cash_generation_summary`
- `manager_comparison`
- `data_confidence_note`

## View Payload Shape

Each view uses `schema_version: report_element_view_payload.v1` and includes:

- `element_id`
- `element_title`
- `template_category`
- `view_type`
- `render_type`
- `as_of_date`
- `headline`
- `summary_text`
- `key_metrics`
- `evidence_rows`
- `detail_tables`
- `caveats`
- `confidence_summary`
- `human_review_items`
- `source_input_path`
- `input_parameters`
- `synthetic_data: true`
- `validation`

`source_input_path` is JSON/source metadata only. Markdown and HTML fragments
must not expose internal JSON paths.

## Markdown And HTML Fragments

Markdown fragments use headings, summary text, small metric tables, evidence
tables, confidence notes, and caveat lists.

HTML fragments are self-contained semantic fragments using `section`, headings,
paragraphs, tables, lists, and small caveat/confidence blocks. They are not full
HTML pages and include no CSS framework, charts, browser app code, or external
assets.

## Supported Initial Element Renderers

`Portfolio Status` renders total synthetic value, cash/cash-like value, manager
and position counts, confidence label, human-review count/value, and manager
value evidence.

`Concentration` renders the selected lens, largest bucket, top buckets, top
holdings, and overlap evidence where available.

`Scenario Impact by Manager` renders the selected scenario name, base value,
scenario value, total impact, impact percent, manager impacts, confidence, and a
not-a-forecast caveat.

`Cash Generation Summary` renders current cash-like value, income/distributions,
transaction flows, fees, period metadata, and manager cash-generation rows.

`Manager Comparison` renders manager mandate/role rows, current value, period
value change, themes, confidence notes, and human-review counts/value.

`Data Confidence Note` renders confidence label, human-review count/value,
confidence buckets, valuation treatment rows, and caveats about source readiness.

Unknown future elements can use a generic fallback renderer, but the six initial
element types should remain element-aware.

## Validation Invariants

`validate_report_element_view(...)` checks that:

- view payloads have required identity, render, headline, summary, metric,
  caveat, confidence, human-review, and synthetic-data fields;
- Markdown and HTML fragments are non-empty when supplied;
- scenario output states that it is not a forecast;
- rendered text avoids production-accuracy, guarantee, and real-data markers;
- user-facing fragments do not expose internal JSON paths.

Validation returns structured `status`, `errors`, `warnings`,
`renderer_version`, and `validated_at` fields.

## Public Functions

The renderer is implemented in `src/arangur/report_elements/rendering.py`:

- `render_report_element_view(input_payload)`
- `render_report_element_markdown(input_payload)`
- `render_report_element_html(input_payload)`
- `render_all_demo_report_element_views(input_dir, output_dir)`
- `validate_report_element_view(view_payload)`

It can run from the repo root:

```powershell
python src\arangur\report_elements\rendering.py
```

## Deliberately Not Implemented Yet

This rendering layer does not implement:

- full client briefing generation;
- briefing set preview or sequence rendering;
- browser composer integration;
- charts or charting dependencies;
- report packages;
- backend persistence;
- Docker/Postgres changes;
- production valuation, accounting, or performance claims;
- live Plaid, vendor market data, external APIs, or real client data.
