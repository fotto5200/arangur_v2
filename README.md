# Arangur v2

Modern restart-oriented rebuild of Arangur.

Start by reading docs/restart/00_READ_ME_FIRST.md.

## Run The Local Demo Pipeline

The first synthetic vertical slice runs entirely from local JSON fixtures. It does not use Plaid, external APIs, credentials, or real client data.

```powershell
python src\arangur\demo_pipeline.py
```

It generates:

- `reports/demo/canonical_portfolio_snapshot.json`
- `reports/demo/valuation_result.json`
- `reports/demo/exposure_overlap_result.json`
- `reports/demo/scenario_result.json`
- `reports/demo/report_package.json`
- `reports/demo/arangur_demo_report.md`
- `reports/demo/arangur_demo_report.html`

Open the Markdown report in an editor or preview pane, or open the HTML report directly in a browser.

Focused checks:

```powershell
python -m unittest tests.test_demo_pipeline
```
