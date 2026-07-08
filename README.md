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

## Generate Arranger Demo Analytic Pack Outputs

The first Arranger analytic pack proof applies `data/analytic_packs/arranger_demo_pack_v1/` to the existing synthetic portfolio, scenario, and valuation fixtures. It writes deterministic local-only analytics outputs. The proof generator itself does not change advisor UI, generated reports, Docker, deployment, live data, or dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.apply_demo_pack
```

This writes:

- `data/simulation/analytics/theme_exposure_summary.json`
- `data/simulation/analytics/manager_theme_overlap_summary.json`
- `data/simulation/analytics/scenario_impact_by_theme_manager.json`
- `data/simulation/analytics/data_confidence_map.json`
- `data/simulation/analytics/cross_scenario_resilience_summary.json`
- `data/simulation/analytics/analytics_output_index.json`

## Generate Synthetic Full Revaluation Bundle

The internal full revaluation skeleton values every synthetic position under a base market state and the supported scenario market states, currently `ai_chip_selloff` and `rate_shock`, then writes comparison, portfolio-summary, and scenario-index artifacts. This is local-only analytics infrastructure; it does not change advisor UI, report views, Docker, deployment, live data, external APIs, or dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.revaluation_runner
```

This writes deterministic fixtures and outputs under `data/simulation/revaluation/`, including `position_valuation_results_base.json`, scenario-specific valuation/comparison/summary files, scenario-specific coverage and bundle manifests, and `revaluation_scenario_index.json`. Existing `ai_chip_selloff` filenames are preserved for compatibility.

## Generate Revaluation Attribution Outputs

The attribution generator aggregates the full revaluation comparison rows into scenario-specific manager, account, sleeve, coverage, confidence, and gross theme outputs, plus thesis-readiness and cross-scenario summary outputs. It stays local-only and does not wire anything into advisor UI or report elements.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.revaluation_attribution
```

This writes deterministic attribution outputs under `data/simulation/revaluation/attribution/`, including `cross_scenario_revaluation_summary.json` for the currently supported full-revaluation scenarios.

## Generate Lean Revaluation Report Mockups

The lean report-view generator turns the two-scenario full-revaluation outputs into compact report input fixtures, report view fixtures, and Markdown product-review mockups. It stays local-only and does not wire anything into Advisor Preview, Populate, Present, generated reports, Docker, deployment, live data, or dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.lean_report_views
```

This writes:

- `data/simulation/report_element_inputs/lean_revaluation_v1/`
- `data/simulation/report_element_views/lean_revaluation_v1/`
- `docs/product/report_mockups/`

## Generate Synthetic Report Prerequisite Pack

The prerequisite-pack generator writes local-only synthetic inputs for the next v2 mockup tranche: cash-flow delivered/support inputs, Manager Role Summary, and Full Lens Exposure. It does not wire anything into Advisor Preview, Populate, Present, generated reports, Docker, deployment, live data, or dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.synthetic_report_prerequisites
```

This writes deterministic JSON under:

- `data/simulation/report_prerequisites/synthetic_report_prerequisite_pack_v1/`

## Generate Synthetic Attribution Prerequisite Pack

The attribution prerequisite-pack generator writes local-only synthetic benchmark, lens-bucket proxy, period return, weight/flow, theme-benchmark detail, decomposition, and manager attribution inputs used by the local attribution mockups. It does not wire Advisor Preview / Populate / Present / generated reports, touch Docker/deployment, use live data, or add dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.synthetic_attribution_prerequisites
```

This writes deterministic JSON under:

- `data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1/`

## Generate Synthetic Attribution Report Mockups

The attribution report-view generator turns the synthetic attribution prerequisite pack into local-only attribution report input fixtures, view fixtures, and Markdown product-review mockups using the polished global/theme/manager benchmark wording. It does not wire anything into Advisor Preview, Populate, Present, generated reports, Docker, deployment, live data, or dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.attribution_report_views
```

This writes:

- `data/simulation/report_element_inputs/attribution_v1/`
- `data/simulation/report_element_views/attribution_v1/`
- `docs/product/report_mockups/attribution_v1/`

## Audit Synthetic Attribution Methodology

The attribution methodology audit summarizes the calculation provenance and known gaps in the current local synthetic attribution artifacts. It is read-only by default and does not regenerate mockups or wire anything into Advisor Preview, Populate, Present, generated reports, Docker, deployment, live data, or dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.attribution_methodology_audit
```

Use `--output path\to\audit_summary.json` only when a local JSON copy is useful. The full methodology note lives at `docs/architecture/attribution_methodology_and_calculation_audit_v1.md`.

## Generate Synthetic Attribution Calculation Inputs

The attribution calculation-input generator writes the lower-level local synthetic inputs needed by a future calculated attribution engine: selected AI Adoption lens policy, theme benchmark weight states, theme benchmark return inputs, compact grouped asset inputs, manager benchmark-basis metadata, residual policy, and readiness status. It does not regenerate attribution mockups, wire Advisor Preview / Populate / Present / generated reports, touch Docker/deployment, use live data, or add dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.synthetic_attribution_calculation_inputs
```

This writes deterministic JSON under:

- `data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1/calculation_inputs/`

## Generate Calculated Synthetic Attribution Outputs

The calculated attribution engine consumes the local synthetic calculation inputs and writes whole-portfolio, theme benchmark, theme asset, manager, and quality/readiness outputs for future attribution mockup regeneration. It does not regenerate attribution mockups, wire Advisor Preview / Populate / Present / generated reports, touch Docker/deployment, use live data, or add dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.calculated_synthetic_attribution
```

This writes deterministic JSON under:

- `data/simulation/attribution_calculated/synthetic_attribution_engine_v1/`

## Generate Revaluation v2 Report Mockups

The v2 report-view generator turns full-revaluation outputs, attribution outputs, and the synthetic prerequisite pack into v2 report input fixtures, v2 report view fixtures, and Markdown product-review mockups, including separate Cash Flow Delivered and Cash-Flow Support Outlook reports. It preserves v1 mockups and does not wire anything into Advisor Preview, Populate, Present, generated reports, Docker, deployment, live data, or dependencies.

```cmd
set PYTHONPATH=src
python -m arangur.analytics.lean_report_views_v2
```

This writes:

- `data/simulation/report_element_inputs/revaluation_v2/`
- `data/simulation/report_element_views/revaluation_v2/`
- `docs/product/report_mockups/revaluation_v2/`

## Map Analytic Outputs To Report Element Views

The analytic report-element mapper turns those proof outputs into separate renderer-ready payloads for Concentration, Manager Comparison, Scenario Impact by Manager, Data Confidence Note, and Portfolio Status. The local Advisor workflow can now consume these committed analytic-derived fragments for supported configured specs without adding backend endpoints, charts, live data, or dependencies.

```powershell
python src\arangur\report_elements\analytic_input_mapping.py
```

To render the analytic payloads:

```cmd
set PYTHONPATH=src
python -c "from arangur.report_elements.rendering import render_all_analytic_report_element_views; render_all_analytic_report_element_views()"
```

This writes separate analytic summaries alongside the existing legacy report-element fixtures:

- `data/simulation/report_element_inputs/report_element_analytic_input_summary.json`
- `data/simulation/report_element_views/report_element_analytic_view_summary.json`

The Builder exposes only curated approved-pack choices, such as approved themes, scenarios, lenses, and confidence focus labels. Preview, Populate, and Present can use the analytic-derived fragments when the selected configuration has a committed demo view; unsupported combinations stay as clean demo placeholders.

For the canonical local analytic demo story and restoreable browser-local workflow fixture, see `docs/demo/analytic_report_demo_story_v1.md` and `docs/demo/analytic_demo_workflow_fixture.json`.

For the internal full portfolio revaluation methodology behind future analytic-pack implementation, see `docs/architecture/arranger_internal_analytics_algorithm_design_v1.md`.

For the key market-state scenario basis design that constructs scenario market states before revaluation, see `docs/architecture/key_market_state_scenario_basis_design_v1.md`.

For the position valuation coverage mapping design that routes positions to instruments, pricing functions, required market inputs, and coverage statuses, see `docs/architecture/position_valuation_coverage_mapping_design_v1.md`.

## Local Report Index

Both demo runner commands refresh a shared static report index:

- `reports/demo/index.html`

To rebuild the index from existing report packages without rerunning analytics:

```powershell
python src\arangur\demo_pipeline.py --build-index
```

Open `reports/demo/index.html` in a browser to browse the native demo and Plaid-shaped mock report runs. The index is local-only and synthetic; it is not an interactive app, does not use live Plaid, and does not use real client data.

## Run The FastAPI App

The first deployable-app shell exposes health, source/workflow discovery, synchronous local workflow runs, local run browsing, static generated report artifacts, and optional briefing spec-set save/load endpoints. Default local mode remains file-backed and synthetic-only; optional Postgres persistence is available for private-demo metadata when configured. Local development does not require Docker, live Plaid, external APIs, real client data, or production authentication.

```powershell
python -m uvicorn arangur.app.main:app --reload --app-dir src
```

Then open:

- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/api/sources`
- `http://127.0.0.1:8000/api/workflows`
- `http://127.0.0.1:8000/api/report-elements`
- `http://127.0.0.1:8000/api/report-elements/scenario_impact_by_manager`
- `http://127.0.0.1:8000/api/briefing-spec-sets`
- `http://127.0.0.1:8000/api/runs`
- `http://127.0.0.1:8000/reports/demo/index.html`
- `http://127.0.0.1:8000/`

## Run The Local Docker Private Demo Stack

The local private-demo stack runs the FastAPI app plus an internal Postgres container. It is for local/private-demo smoke testing only. Do not put real secrets, real client data, live Plaid data, or live market data in this stack.

Frank verified this local Docker runtime smoke on 2026-07-02: the app and Postgres came up locally, `/api/health` returned `status: ok`, health confirmed `app_env: private_demo`, `runtime_mode: private_demo`, `db_engine: postgres`, and `database_configured: true`, `/app/` loaded, and a Postgres-backed briefing spec-set POST/list smoke worked. This is still local/private-demo readiness only; it is not a public deployment, production authentication, real-client-data path, generated report history, Caddy/Lightsail/Cloudflare setup, or production report system.

Start the stack from the repo root:

```cmd
copy .env.private-demo.example .env.private-demo
docker compose --env-file .env.private-demo up --build
```

In another cmd, run the local preflight smoke script:

```cmd
scripts\private_demo_smoke.cmd
```

The smoke script expects the stack to already be running. It uses `curl.exe` only, checks `/api/health`, `/app/`, `/api/report-elements`, and saves/lists a small synthetic briefing spec-set payload through `/api/briefing-spec-sets`. It does not use real client data, real market data, live Plaid, external APIs, or public deployment infrastructure.

For the operator click-through and pass/fail checklist, see `docs/demo/private_demo_walkthrough.md`.

Open the browser composer:

```cmd
start "" http://127.0.0.1:8000/app/
```

Stop the stack:

```cmd
docker compose --env-file .env.private-demo down
```

Or use the helper:

```cmd
scripts\private_demo_down.cmd
```

To reset the local demo database volume:

```cmd
scripts\private_demo_down.cmd --reset
```

The reset helper asks for confirmation before running `docker compose --env-file .env.private-demo down -v`, which deletes the local Postgres demo volume. If Docker reports that the daemon or Linux engine is unavailable, start Docker Desktop, wait until the Linux engine is running, and rerun the `docker compose` command. If port `8000` is already in use, stop the other local app or service before starting this stack. If a curl smoke check fails, confirm the stack is still running and inspect logs with `docker compose --env-file .env.private-demo logs app`. Never commit `.env.private-demo`; it is a local copy only.

Compose sets `DB_ENGINE=postgres` and `DATABASE_URL` for the app container. The app safely creates the existing workflow-run and briefing spec-set tables with `CREATE TABLE IF NOT EXISTS` on startup. The browser Developer / QA backend save/load controls can exercise Postgres-backed briefing spec-set save/load in this local stack. See `docs/deployment/private_demo_docker.md` for the full smoke checklist and seed payload details.

## Run The Report Element Spec Composer

For a fresh checkout, install the current lightweight Python requirements:

```cmd
python -m pip install -r requirements.txt
```

Start the FastAPI app:

```cmd
python -m uvicorn arangur.app.main:app --reload --app-dir src
```

Open `http://127.0.0.1:8000/app/` to use the Report Element Finder / Composer prototype. It lands on Advisor Home with exactly four product choices: Create a new workflow, Work with an existing workflow, Populate a workflow with data, and Present / view reports. The static app uses hash routes such as `#home`, `#workflow/existing`, `#workflow/populate`, `#workflow/present`, `#builder`, `#populate`, `#presentation`, `#preview/client`, `#preview/advisor`, and `#advanced` so browser Back moves between the advisor choice, chooser, builder, populate, presentation, and preview surfaces.

Create a new workflow reveals only the workflow-type choices: New Client Briefing Workflow and New Advisor Review Workflow. Work with an existing workflow is the edit/design path for browser-local saved workflows, including open-to-edit, copy, and delete.

Populate a workflow with data lets the advisor choose a saved workflow, use the current synthetic demo data snapshot, and create a demo generated report artifact without entering Builder/edit mode. The artifact is returned by `POST /api/generated-reports/demo-populate`, opened in a clean demo populated report view, and saved only in this browser under `localStorage` key `arangur.local_generated_reports.v1` for Present / view reports. It is not saved to backend generated report history or a report library.

The Builder workspace keeps the compact static client context line, asks the advisor to choose or switch the Client Briefing Workflow or Advisor Review Workflow target, loads the report element template catalog from `/api/report-elements`, and provides search, category browsing, lightweight filters, and an attached compact grouped `Browse all templates` picker without showing the full catalog as large cards or an inline catalog list.

Discovery controls help locate templates; they are not saved as report specs. After a template is selected, the right side shows a short preview and a `Use this element` action. The configuration step then renders only the fields that template needs, with placement shown separately as `Add to set as`. Scope, lens, metric/measure, scenario, display, and advisor internal purpose are template-driven rather than universal form fields. For demo-rendered analytic elements, scope choices are limited to scopes with committed preview fixtures; selected manager/account/sleeve/strategy scopes remain modeled in the composer but are guarded when a selected-scope preview fixture is not available. Cash Generation Summary currently previews only at the whole-portfolio cash-summary level, so the UI does not present a separate all-managers cash scope that would render the same demo output.

Configured analytic elements can be added to either the Client Briefing Workflow or the Advisor Review Workflow. Advisors can also add manual narrative elements such as section titles, explanations, discussion prompts, speaker notes, working notes, and follow-up items. Analytic and narrative elements live in the same ordered local workflow lists and can be edited, duplicated, moved, or removed.

When a configured analytic spec matches a committed rendered demo view and supported preview scope, the row shows that it is previewable. Specs that do not match the current fixture set, or that carry a selected scope the demo cannot render, are flagged before preview as not previewable yet, with advisor-facing guidance to edit, replace, remove, or keep them out of the preview. Individual element preview is available as a secondary element tool.

The main advisor flow is Advisor Home -> choose intent -> Builder, Populate, Presentation view, or Preview -> edit when needed. Use `Preview Client Briefing` or `Preview Advisor Review` from the Builder to open a focused preview surface for the current ordered workflow. Empty workflows are not previewed; the builder asks for at least one client briefing or advisor review element first.

Matching analytic specs use committed rendered demo element views, including analytic-derived fragments for supported Arranger Demo Analytic Pack choices; unsupported preview sections use the nontechnical placeholder `This section is not available in the demo preview.` Unsupported populated-report sections use `This section is not available in the demo generated report.` Narrative elements render as briefing text rather than metadata rows. Generated report artifacts preserve the advisor-authored workflow body sequence: narrative section titles/text stay as authored, selected template titles stay intact, and matched analytic elements reuse the rendered fragment detail shown in Preview. Generated reports do not auto-add framing, closing prompts, follow-ups, or caveat body sections; source workflow, generated timestamp, data snapshot, and synthetic-demo caveat remain report metadata/header-footer content. The preview surface shows only Back to Builder, Print, Export HTML, Copy text, and a compact demo caveat. The populated report view shows Back to Home, Back to Workflow, Print, Export HTML, Copy text, ordered workflow sections, and concise metadata. Present / view reports lists browser-local generated report artifacts created by Populate and opens a clean Generated report presentation view with source workflow, report type, generated/data-as-of metadata, Back to Home, Back to Reports, Print, Export HTML, and Copy text.

Named saved workflows are browser-local draft workflow definitions stored in `localStorage` under `arangur.local_named_briefing_workflows.v1`. Saved workflow records preserve a human-readable `display_name` such as `Report Number 2` separately from the internal `workflow_id` / `storage_key`, plus local timestamps and a simple workflow type label. `Save` updates the currently open workflow under the same `workflow_id` without changing `display_name`; `Rename` changes the display name for that same workflow id and blocks duplicate names; `Save As New` creates a separate workflow with a new id; and `Copy Workflow` / saved-list copy creates a readable copy such as `Report Number 2 Copy` while leaving the original listed. Saved workflows wrap the same local spec-set payload shape used for JSON transfer, can be opened to edit, deleted, and populated with current demo data. Generated report shelf records are stored separately by artifact `report_id`; deleting a generated report shelf record does not delete its source workflow.

Developer / QA tools are secondary to the four product choices. They contain local workflow JSON copy/download/restore, technical local export details, optional backend save/load test controls, and QA reference preview links. The current unsaved Client Briefing Workflow and Advisor Review Workflow can still be copied or downloaded as local workflow JSON using schema `arangur.local_briefing_spec_set.v1` after at least one element has been added. Local export/download remains available in all modes and does not create database records.

The optional Developer / QA backend save/load tool can save or reopen the same briefing spec-set payload through `/api/briefing-spec-sets` when Postgres persistence is configured. In default local mode, the page shows `Backend persistence is not configured. Use local workflow JSON export/download for now.` and browser-local named workflow saving plus local workflow JSON copy/download/restore remain the intended fallback.

The app serves committed synthetic simulation artifacts under `/simulation/...` for this local preview flow. It does not serve the whole repo and does not expose credentials or real data.

This UI does not generate charts or server-side preview files from the local set. It does not call the workflow-run API or show report-package links. Populate can create a browser-local generated report artifact shelf record from a saved workflow and the current synthetic demo snapshot, but it does not persist generated artifacts to the backend, build a report library, or create report history. Backend briefing spec-set persistence is draft metadata only; durable production records and server-side report generation remain future work after product and data-model decisions are stable.

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

With `DB_ENGINE=none`, no database is required. Workflow runs still generate local artifacts and `/api/runs` scans `reports/demo/**/report_package.json`. `/api/briefing-spec-sets` returns an empty saved-set list and save attempts return a not-configured message after validating the browser-local payload.

The private-demo persistence skeleton can use Postgres through the local Docker stack or another explicitly configured Postgres instance:

```cmd
set DB_ENGINE=postgres
set DATABASE_URL=postgresql://arangur_demo:password@postgres:5432/arangur_private_demo
python -m uvicorn arangur.app.main:app --reload --app-dir src
```

When `DB_ENGINE=postgres` and `DATABASE_URL` are set, the app creates minimal `workflow_run`, `report_artifact`, `run_event`, `briefing_spec_set`, and `briefing_spec_item` tables if missing. Workflow runs persist run metadata plus artifact links after local report generation. Briefing spec-set save/load persists draft browser-composer payloads and derived item summaries. Postgres is not required for ordinary local tests.

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
- `docs/product/report_purpose_information_economy_audit_v1.md`
- `docs/product/report_system_redesign_blueprint_v1.md`
- `docs/product/report_family_catalog_v1.md`
- `docs/product/revised_report_mockup_spec_v2.md`
- `docs/architecture/arranger_control_plane_boundary_v1.md`
- `docs/architecture/arranger_internal_analytics_algorithm_design_v1.md`
- `docs/architecture/key_market_state_scenario_basis_design_v1.md`
- `docs/architecture/thesis_lens_position_mapping_design_v1.md`
- `docs/architecture/position_valuation_coverage_mapping_design_v1.md`
- `docs/architecture/report_data_and_analytics_requirements_v1.md`
- `docs/architecture/simulation_kernel_three_surface_model_v1.md`
- `docs/architecture/deployable_demo_app_architecture.md`
- `docs/architecture/persistence_model_plan.md`
- `docs/contracts/analytic_pack_contract_v1.md`
- `docs/contracts/simulation_kernel_contracts_v1.md`
- `docs/contracts/synthetic_position_universe_contract_v1.md`
- `docs/contracts/synthetic_market_state_contract_v1.md`
- `docs/contracts/simplified_daily_valuation_contract_v1.md`
- `docs/contracts/report_element_input_mapping_contract_v1.md`
- `docs/contracts/report_element_rendering_contract_v1.md`
- `docs/contracts/briefing_set_preview_contract_v1.md`
- `docs/contracts/local_briefing_spec_set_contract_v1.md`
- `docs/contracts/briefing_spec_set_persistence_contract_v1.md`
- `docs/contracts/workflow_run_persistence_contract.md`
- `docs/contracts/report_element_template_catalog_contract.md`
- `docs/decisions/0003_three_surface_simulation_kernel.md`
- `docs/deployment/private_demo_stack_plan.md`
- `docs/deployment/private_demo_docker.md`
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
