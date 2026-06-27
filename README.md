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
- `reports/demo/report_package.json`
- `reports/demo/arangur_demo_report.md`
- `reports/demo/arangur_demo_report.html`

The Plaid-shaped mock path generates the same artifact names under `reports/demo/plaid_mock/`.

Non-default native workflows generate under `reports/demo/workflows/<workflow>/`. Non-default Plaid-shaped workflows generate under `reports/demo/plaid_mock/workflows/<workflow>/`.

Open the Markdown report in an editor or preview pane, or open the HTML report directly in a browser.

## Local Report Index

Both demo runner commands refresh a shared static report index:

- `reports/demo/index.html`

To rebuild the index from existing report packages without rerunning analytics:

```powershell
python src\arangur\demo_pipeline.py --build-index
```

Open `reports/demo/index.html` in a browser to browse the native demo and Plaid-shaped mock report runs. The index is local-only and synthetic; it is not an interactive app, does not use live Plaid, and does not use real client data.

## Design Roadmaps

Future scenario and data-coverage work is captured in:

- `docs/architecture/scenario_engine_roadmap.md`
- `docs/architecture/data_availability_workstream.md`
- `docs/demo/report_workflow_implications.md`

Focused checks:

```powershell
python -m unittest tests.test_demo_pipeline
python -m unittest tests.test_plaid_mock_pipeline
python -m unittest tests.test_report_index
python -m unittest tests.test_workflow_templates
```
