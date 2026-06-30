# Arangur v2

Modern restart-oriented rebuild of Arangur.

Start by reading docs/restart/00_READ_ME_FIRST.md.

## Run The Local Demo Pipeline

The first synthetic vertical slice runs entirely from local JSON fixtures. It does not use Plaid, external APIs, credentials, or real client data.

```powershell
python src\arangur\demo_pipeline.py
```

To run the Plaid-shaped mock ingestion path:

```powershell
python src\arangur\demo_pipeline.py --source plaid_mock
```

To render a workflow-specific report:

```powershell
python src\arangur\demo_pipeline.py --workflow manager_overlap_review
python src\arangur\demo_pipeline.py --workflow scenario_risk_review
python src\arangur\demo_pipeline.py --workflow data_coverage_review
python src\arangur\demo_pipeline.py --source plaid_mock --workflow intake_review
```

The Plaid-shaped path uses only `data/demo/plaid_mock_investments.json`. It does not use live Plaid, Plaid Sandbox, Plaid Link, access tokens, credentials, or real account data.

The default demo generates:

- `reports/demo/canonical_portfolio_snapshot.json`
- `reports/demo/valuation_result.json`
- `reports/demo/exposure_overlap_result.json`
- `reports/demo/scenario_result.json`
- `reports/demo/data_coverage_result.json`
- `reports/demo/report_package.json`
- `reports/demo/arangur_demo_report.md`
- `reports/demo/arangur_demo_report.html`

The Plaid-shaped mock path generates the same artifact names under `reports/demo/plaid_mock/`.

Non-default native workflows generate under `reports/demo/workflows/<workflow>/`. Non-default Plaid-shaped workflows generate under `reports/demo/plaid_mock/workflows/<workflow>/`.

`data_coverage_result.json` is a local-only valuation confidence prototype. It labels identifier, price, classification, source transparency, valuation method, and scenario mapping coverage as high, medium, low, or unknown, and surfaces human-review items. It does not use live market data, live Plaid, vendor data, or real client data.

Open the Markdown report in an editor or preview pane, or open the HTML report directly in a browser.

## Generate The Synthetic Position Universe

The first simulation-kernel surface generates a deterministic synthetic multi-manager position universe. It is independent from the current report pipeline and does not generate prices, market-state histories, scenario paths, or valuation outputs.

```powershell
python src\arangur\simulation\synthetic_position_universe_generator.py
```

This writes:

- `data/simulation/synthetic_position_universe.json`
- `data/simulation/synthetic_position_universe_summary.json`

The universe includes synthetic managers, accounts/sleeves, instruments, 74 positions, 90-day transaction traces, themes/lenses, data-quality flags, human-review items, and future market-state requirements for later simulation batches.

## Generate The Synthetic Market State

The second simulation-kernel surface consumes the synthetic position universe and generates deterministic synthetic market/state-of-world fixtures. It produces direct prices, proxy state, rates/FX/spread/volatility proxies, private and stale mark treatments, confidence flags, proxy mappings, historical paths, scenario market states, and a covariance recovery check. It does not generate position values, portfolio values, value-change packages, reports, charts, live market data, vendor data, external API calls, or real client data.

```powershell
python src\arangur\simulation\synthetic_market_state_generator.py
```

This writes:

- `data/simulation/synthetic_market_state_history.json`
- `data/simulation/synthetic_market_state_summary.json`
- `data/simulation/synthetic_scenario_market_states.json`

The default fixture covers 91 calendar dates, 12 core drivers, all 23 market-state variables required by the synthetic position universe, and five scenarios: AI/chip selloff, rate shock, energy shock, private-market liquidity freeze, and Taiwan disruption.

## Generate The Simplified Daily Valuation Outputs

The third simulation-kernel surface consumes the synthetic position universe, market-state history, and scenario market states. It generates deterministic simplified economic daily valuations, value-change packages, scenario revaluation outputs, confidence summaries, and validation results. It does not implement production accounting, tax lots, settlement reconciliation, full fixed-income/private-asset accounting, UI changes, report generation, live data, external APIs, or real client data.

```powershell
python src\arangur\simulation\simplified_daily_valuation_engine.py
```

This writes:

- `data/simulation/daily_position_valuation_history.json`
- `data/simulation/daily_portfolio_valuation_history.json`
- `data/simulation/value_change_package.json`
- `data/simulation/scenario_revaluation_results.json`
- `data/simulation/simplified_valuation_summary.json`

The default fixture values 74 positions over 91 dates, emits one daily portfolio valuation per market-state date, revalues all five scenarios, and keeps transaction/flow effects separate from synthetic economic value movement.

## Generate Report Element Input Payloads

The first report-element input mapping layer consumes the synthetic simulation fixtures and writes structured renderer-ready inputs for the initial report-element templates. It does not generate final reports, charts, browser UI, client briefings, persistence records, live data calls, or external API calls.

```powershell
python src\arangur\report_elements\input_mapping.py
```

This writes:

- `data/simulation/report_element_inputs/portfolio_status.json`
- `data/simulation/report_element_inputs/concentration_theme.json`
- `data/simulation/report_element_inputs/concentration_sector_industry.json`
- `data/simulation/report_element_inputs/scenario_impact_by_manager_ai_chip_selloff.json`
- `data/simulation/report_element_inputs/cash_generation_summary.json`
- `data/simulation/report_element_inputs/manager_comparison.json`
- `data/simulation/report_element_inputs/data_confidence_note.json`
- `data/simulation/report_element_inputs/report_element_input_summary.json`

The default fixtures map Portfolio Status, Concentration, Scenario Impact by Manager, Cash Generation Summary, Manager Comparison, and Data Confidence Note to structured metrics, evidence rows, tables, confidence summaries, caveats, and human-review items.

## Render Report Element View Fragments

The first report-element rendering layer consumes the input payloads and writes simple deterministic view JSON plus Markdown and HTML fragments. These are reviewable fragments for later briefing-set preview. They are not full client briefings, charts, browser UI state, persistence records, report packages, live data calls, or production reports.

```powershell
python src\arangur\report_elements\rendering.py
```

This writes:

- `data/simulation/report_element_views/portfolio_status.view.json`
- `data/simulation/report_element_views/portfolio_status.md`
- `data/simulation/report_element_views/portfolio_status.html`
- `data/simulation/report_element_views/concentration_theme.view.json`
- `data/simulation/report_element_views/concentration_theme.md`
- `data/simulation/report_element_views/concentration_theme.html`
- `data/simulation/report_element_views/concentration_sector_industry.view.json`
- `data/simulation/report_element_views/concentration_sector_industry.md`
- `data/simulation/report_element_views/concentration_sector_industry.html`
- `data/simulation/report_element_views/scenario_impact_by_manager_ai_chip_selloff.view.json`
- `data/simulation/report_element_views/scenario_impact_by_manager_ai_chip_selloff.md`
- `data/simulation/report_element_views/scenario_impact_by_manager_ai_chip_selloff.html`
- `data/simulation/report_element_views/cash_generation_summary.view.json`
- `data/simulation/report_element_views/cash_generation_summary.md`
- `data/simulation/report_element_views/cash_generation_summary.html`
- `data/simulation/report_element_views/manager_comparison.view.json`
- `data/simulation/report_element_views/manager_comparison.md`
- `data/simulation/report_element_views/manager_comparison.html`
- `data/simulation/report_element_views/data_confidence_note.view.json`
- `data/simulation/report_element_views/data_confidence_note.md`
- `data/simulation/report_element_views/data_confidence_note.html`
- `data/simulation/report_element_views/report_element_view_summary.json`

## Assemble Briefing Set Previews

The first briefing-set preview layer consumes rendered report element views and writes deterministic file-based Client Briefing Set and Advisor Review Set previews. These previews prove that rendered elements can be composed into ordered sets. They are not browser UI integration, persisted briefing sets, charts, report packages, live data calls, or production client-ready reports.

```powershell
python src\arangur\report_elements\briefing_set_preview.py
```

This writes:

- `data/simulation/briefing_set_previews/client_briefing_set_preview.json`
- `data/simulation/briefing_set_previews/client_briefing_set_preview.md`
- `data/simulation/briefing_set_previews/client_briefing_set_preview.html`
- `data/simulation/briefing_set_previews/advisor_review_set_preview.json`
- `data/simulation/briefing_set_previews/advisor_review_set_preview.md`
- `data/simulation/briefing_set_previews/advisor_review_set_preview.html`
- `data/simulation/briefing_set_previews/briefing_set_preview_index.json`
- `data/simulation/briefing_set_previews/index.html`

The client preview uses Portfolio Status, Concentration by Theme, Scenario Impact by Manager, and Data Confidence Note. The advisor preview uses Manager Comparison, Cash Generation Summary, Concentration by Sector/Industry, Scenario Impact by Manager, and Data Confidence Note.

## Local Report Index

Both demo runner commands refresh a shared static report index:

- `reports/demo/index.html`

To rebuild the index from existing report packages without rerunning analytics:

```powershell
python src\arangur\demo_pipeline.py --build-index
```

Open `reports/demo/index.html` in a browser to browse the native demo and Plaid-shaped mock report runs. The index is local-only and synthetic; it is not an interactive app, does not use live Plaid, and does not use real client data.

## Run The FastAPI App

The first deployable-app shell exposes health, source/workflow discovery, synchronous local workflow runs, local run browsing, and static generated report artifacts. It remains file-backed and synthetic-only; it does not use Postgres, Docker, live Plaid, external APIs, real client data, or production authentication yet.

```powershell
python -m uvicorn arangur.app.main:app --reload --app-dir src
```

Then open:

- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/api/sources`
- `http://127.0.0.1:8000/api/workflows`
- `http://127.0.0.1:8000/api/report-elements`
- `http://127.0.0.1:8000/api/report-elements/scenario_impact_by_manager`
- `http://127.0.0.1:8000/api/runs`
- `http://127.0.0.1:8000/reports/demo/index.html`
- `http://127.0.0.1:8000/`

## Run The Report Element Spec Composer

For a fresh checkout, install the current lightweight Python requirements:

```cmd
python -m pip install -r requirements.txt
```

Start the FastAPI app:

```cmd
python -m uvicorn arangur.app.main:app --reload --app-dir src
```

Open `http://127.0.0.1:8000/app/` to use the Report Element Finder / Composer prototype. It starts with a compact static client context line, asks the advisor to choose the target set, loads the report element template catalog from `/api/report-elements`, and provides search, category browsing, lightweight filters, and an attached compact grouped `Browse all templates` picker without showing the full catalog as large cards or an inline catalog list.

Discovery controls help locate templates; they are not saved as report specs. After a template is selected, the right side shows a short preview and a `Use this element` action. The configuration step then renders only the fields that template needs, with placement shown separately as `Add to set as`. Scope, lens, metric/measure, scenario, display, and advisor internal purpose are template-driven rather than universal form fields.

Configured analytic elements can be added to either the Client Briefing Set or the Advisor Review Set. Advisors can also add manual narrative elements such as section titles, explanations, discussion prompts, speaker notes, working notes, and follow-up items. Analytic and narrative elements live in the same ordered local set lists and can be edited, duplicated, moved, or removed.

When a configured analytic spec matches a committed rendered demo view, the row shows `Preview available` and can open the rendered element fragment in a small one-element preview panel. Specs that do not match the current deterministic fixture set show `Preview not available yet for this spec.` The app also links to the static sample Client Briefing Set and Advisor Review Set previews generated under `data/simulation/briefing_set_previews/`; those samples come from current deterministic demo outputs, not from the unsaved local composer set.

The current unsaved Client Briefing Set and Advisor Review Set can be copied or downloaded as a browser-local spec-set export using schema `arangur.local_briefing_spec_set.v1` after at least one element has been added. A collapsed `Technical local export details` panel and `Restore local spec set` control are available for local handoff and restart testing. This export is not backend persistence and does not create database records.

Use `Preview Client Briefing Set` or `Preview Advisor Review Set` to assemble the current local ordered set in the browser. Matching analytic specs use existing rendered demo element views; unmatched specs show placeholders, and narrative elements render as local text. This current-set preview is separate from the deterministic sample preview files.

After a non-empty current local preview is open, secondary controls can print the selected Client Briefing Set or Advisor Review Set, download a standalone HTML preview, or copy plain preview text. The print path uses the browser's normal Print to PDF flow and hides composer controls, JSON details, artifact paths, and edit controls. The downloaded HTML is created with browser-local Blob/download behavior from the current local state and existing rendered demo fragments; it is not written by the server and is not persisted.

The app serves committed synthetic simulation artifacts under `/simulation/...` for this local preview flow. It does not serve the whole repo and does not expose credentials or real data.

This UI does not generate reports, charts, or persisted specs from the local set. It does not call the workflow API or show report-package links. Backend persistence, durable export records, and server-side report generation remain future work after product and data-model decisions are stable.

Create a native demo manager-overlap workflow run:

```cmd
curl.exe -X POST http://127.0.0.1:8000/api/runs -H "Content-Type: application/json" -d "{\"source\":\"native_demo\",\"workflow\":\"manager_overlap_review\"}"
```

Create a Plaid-shaped mock intake workflow run:

```cmd
curl.exe -X POST http://127.0.0.1:8000/api/runs -H "Content-Type: application/json" -d "{\"source\":\"plaid_mock\",\"workflow\":\"intake_review\"}"
```

Generated report artifacts are served only from `reports/demo/` under matching URLs such as `/reports/demo/workflows/manager_overlap_review/arangur_demo_report.html`.

## Persistence Settings

Local development defaults to file-backed mode:

```cmd
set DB_ENGINE=none
python -m uvicorn arangur.app.main:app --reload --app-dir src
```

With `DB_ENGINE=none`, no database is required. Workflow runs still generate local artifacts and `/api/runs` scans `reports/demo/**/report_package.json`.

The first private-demo persistence skeleton can use Postgres when a later Docker/private-demo batch provides the database:

```cmd
set DB_ENGINE=postgres
set DATABASE_URL=postgresql://arangur_demo:password@postgres:5432/arangur_private_demo
python -m uvicorn arangur.app.main:app --reload --app-dir src
```

When `DB_ENGINE=postgres` and `DATABASE_URL` are set, the app creates minimal `workflow_run`, `report_artifact`, and `run_event` tables if missing and persists run metadata plus artifact links after local report generation. Postgres is not required for ordinary local tests.

## Design Roadmaps

Future scenario, data-coverage, and deployable private-demo work is captured in:

- `docs/ui_reporting/ui_reporting_philosophy_v1.md`
- `docs/ui_reporting/briefing_story_model_v1.md`
- `docs/ui_reporting/demo_console_redesign_brief_v1.md`
- `docs/ui_reporting/guided_briefing_builder_correction_v1.md`
- `docs/ui_reporting/briefing_set_builder_model_v1.md`
- `docs/ui_reporting/briefing_set_report_view_model_v1.md`
- `docs/ui_reporting/briefing_set_client_preview_model_v1.md`
- `docs/ui_reporting/briefing_set_builder_implementation_brief_v1.md`
- `docs/ui_reporting/report_element_finder_composer_current_model_v1.md`
- `docs/ui_reporting/client_briefing_page_model_v1.md`
- `docs/ui_reporting/manager_role_review_v1.md`
- `docs/architecture/simulation_kernel_three_surface_model_v1.md`
- `docs/architecture/deployable_demo_app_architecture.md`
- `docs/architecture/persistence_model_plan.md`
- `docs/contracts/simulation_kernel_contracts_v1.md`
- `docs/contracts/synthetic_position_universe_contract_v1.md`
- `docs/contracts/synthetic_market_state_contract_v1.md`
- `docs/contracts/simplified_daily_valuation_contract_v1.md`
- `docs/contracts/report_element_input_mapping_contract_v1.md`
- `docs/contracts/report_element_rendering_contract_v1.md`
- `docs/contracts/briefing_set_preview_contract_v1.md`
- `docs/contracts/local_briefing_spec_set_contract_v1.md`
- `docs/contracts/workflow_run_persistence_contract.md`
- `docs/contracts/report_element_template_catalog_contract.md`
- `docs/decisions/0003_three_surface_simulation_kernel.md`
- `docs/deployment/private_demo_stack_plan.md`
- `docs/decisions/0002_copy_education_private_demo_stack.md`
- `docs/architecture/scenario_engine_roadmap.md`
- `docs/architecture/data_availability_workstream.md`
- `docs/contracts/data_coverage_result_contract.md`
- `docs/demo/report_workflow_implications.md`

Focused checks:

```powershell
python -m unittest tests.test_demo_pipeline
python -m unittest tests.test_plaid_mock_pipeline
python -m unittest tests.test_report_index
python -m unittest tests.test_workflow_templates
python -m unittest tests.test_data_coverage
python -m unittest tests.test_synthetic_position_universe
python -m unittest tests.test_synthetic_market_state
python -m unittest tests.test_simplified_daily_valuation
python -m unittest tests.test_report_element_input_mapping
python -m unittest tests.test_report_element_rendering
python -m unittest tests.test_briefing_set_preview
python -m unittest tests.test_app_health
python -m unittest tests.test_report_element_catalog
python -m unittest tests.test_app_runs_api
python -m unittest tests.test_app_persistence
```
