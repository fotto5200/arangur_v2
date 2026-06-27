# Restart Includes

Use these file sets when starting different kinds of sessions.

## Minimal ChatGPT Strategy Restart

- `docs/restart/00_READ_ME_FIRST.md`
- `docs/restart/01_project_profile.md`
- `docs/restart/02_development_method.md`
- `docs/restart/05_decision_log.md`
- `docs/restart/07_active_workstreams.md`
- `docs/restart/08_next_actions.md`
- `docs/restart/CURRENT_STATE.md`

## Codex Implementation Restart

- `README.md`
- `docs/restart/00_READ_ME_FIRST.md`
- `docs/restart/01_project_profile.md`
- `docs/restart/02_development_method.md`
- `docs/restart/03_architecture_current.md`
- `docs/restart/04_component_contracts.md`
- `docs/restart/05_decision_log.md`
- `docs/restart/06_current_repo_map.md`
- `docs/restart/07_active_workstreams.md`
- `docs/restart/08_next_actions.md`
- `docs/restart/CURRENT_STATE.md`

## Demo-System Implementation Restart

- All Codex implementation restart files.
- Future files under `docs/contracts/`.
- Future files under `docs/demo/`.
- Future synthetic fixtures under `data/demo/`.
- Future source files under `src/`.
- Future tests under `tests/`.

## Plaid Integration Restart

- All Codex implementation restart files.
- `docs/contracts/plaid_mock_ingestion_contract.md`.
- Future Plaid architecture notes under `docs/architecture/`.
- `data/demo/plaid_mock_investments.json`.
- `src/arangur/plaid_mock_adapter.py`.
- `src/arangur/demo_pipeline.py`.
- `tests/test_plaid_mock_pipeline.py`.
- Do not include real credentials, `.env` files, auth tokens, or client data.

## MATLAB Audit Restart

- `docs/restart/00_READ_ME_FIRST.md`
- `docs/restart/01_project_profile.md`
- `docs/restart/02_development_method.md`
- `docs/restart/03_architecture_current.md`
- `docs/restart/05_decision_log.md`
- `docs/restart/CURRENT_STATE.md`
- Any future authorized MATLAB audit instructions under `docs/architecture/` or `docs/decisions/`.
- Legacy MATLAB files only when Frank or ChatGPT has authorized a specific audit batch.

## Reporting / Advisor-Assistant Restart

- All Codex implementation restart files.
- Future report contracts under `docs/contracts/`.
- Future report examples under `docs/demo/`.
- Future generated demo report packages under `reports/demo/`.
- Future reporting and assistant source files under `src/`.

## Scenario Engine Restart

- All Codex implementation restart files.
- `docs/architecture/thin_demo_system_architecture.md`.
- `docs/architecture/scenario_engine_roadmap.md`.
- `docs/contracts/analytics_outputs_contract.md`.
- `docs/demo/demo_portfolio_storyline.md`.
- `docs/demo/report_workflow_implications.md`.
- Current scenario fixtures under `data/demo/` if implementation is authorized.
- Do not include external scenario-source data, licensed market data, real client data, credentials, or live API access.

## Data Availability / Practicum Restart

- All Codex implementation restart files.
- `docs/architecture/data_availability_workstream.md`.
- `docs/demo/report_workflow_implications.md`.
- `docs/contracts/report_package_contract.md`.
- Future synthetic data coverage fixtures under `data/demo/` if implementation is authorized.
- Do not include real client statements, credentials, manager portal access, private keys, or restricted vendor data.

## Workflow Report Simulation Restart

- All Codex implementation restart files.
- `docs/demo/report_workflow_implications.md`.
- `docs/architecture/scenario_engine_roadmap.md`.
- `docs/architecture/data_availability_workstream.md`.
- `src/arangur/workflow_templates.py`.
- `src/arangur/demo_pipeline.py`.
- `src/arangur/report_generator.py`.
- `src/arangur/report_index.py`.
- Existing generated report package examples under `reports/demo/`.
- Do not include production UI work, real client data, live Plaid, or external APIs.
