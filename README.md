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

This UI does not generate reports, charts, or client preview output yet. It does not call the workflow API or show report links. The next UI batch should serialize/export completed local spec sets without report generation; backend persistence remains a later batch.

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
- `docs/architecture/deployable_demo_app_architecture.md`
- `docs/architecture/persistence_model_plan.md`
- `docs/contracts/workflow_run_persistence_contract.md`
- `docs/contracts/report_element_template_catalog_contract.md`
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
python -m unittest tests.test_app_health
python -m unittest tests.test_report_element_catalog
python -m unittest tests.test_app_runs_api
python -m unittest tests.test_app_persistence
```
