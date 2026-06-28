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
- `docs/ui_reporting/`.
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
- `docs/contracts/data_coverage_result_contract.md`.
- `docs/contracts/report_package_contract.md`.
- `src/arangur/data_coverage.py`.
- `src/arangur/demo_pipeline.py`.
- `src/arangur/report_generator.py`.
- `src/arangur/report_index.py`.
- `tests/test_data_coverage.py`.
- Current synthetic data coverage fixtures under `data/demo/`.
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

## Deployable Demo App Restart

- All Codex implementation restart files.
- `docs/architecture/deployable_demo_app_architecture.md`.
- `docs/deployment/private_demo_stack_plan.md`.
- `docs/decisions/0002_copy_education_private_demo_stack.md`.
- `docs/architecture/persistence_model_plan.md`.
- `docs/demo/report_workflow_implications.md`.
- `requirements.txt`.
- `src/arangur/app/`.
- Existing pipeline modules under `src/arangur/`.
- `tests/test_app_health.py`.
- `tests/test_app_runs_api.py`.
- Existing generated report package examples under `reports/demo/`.
- Do not include real client data, live Plaid, external APIs, credentials, or legacy MATLAB.

## Persistence Implementation Restart

- All Codex implementation restart files.
- `docs/architecture/persistence_model_plan.md`.
- `docs/architecture/deployable_demo_app_architecture.md`.
- `docs/deployment/private_demo_stack_plan.md`.
- `docs/contracts/workflow_run_persistence_contract.md`.
- `docs/contracts/report_package_contract.md`.
- `docs/contracts/data_coverage_result_contract.md`.
- `src/arangur/app/persistence.py`.
- `tests/test_app_persistence.py`.
- Current JSON artifact examples under `reports/demo/`.
- Do not model real client accounts, persist credentials, or decompose full holdings/tax lots unless specifically authorized.

## Docker / Private-Demo Restart

- All Codex implementation restart files.
- `docs/deployment/private_demo_stack_plan.md`.
- `docs/architecture/deployable_demo_app_architecture.md`.
- `docs/decisions/0002_copy_education_private_demo_stack.md`.
- `requirements.txt`.
- `src/arangur/app/`.
- Future Docker and env example files once implemented.
- Do not include `.env.private-demo`, real host credentials, Cloudflare tokens, private keys, or actual production secrets.

## UI Reporting / Briefing Restart

- All Codex implementation restart files.
- `docs/ui_reporting/ui_reporting_philosophy_v1.md`.
- `docs/ui_reporting/briefing_story_model_v1.md`.
- `docs/ui_reporting/audience_depth_modes_v1.md`.
- `docs/ui_reporting/first_demo_briefing_paths_v1.md`.
- `docs/ui_reporting/demo_console_redesign_brief_v1.md`.
- `docs/ui_reporting/manager_role_review_v1.md`.
- `docs/demo/report_workflow_implications.md`.
- `docs/architecture/deployable_demo_app_architecture.md`.
- `src/arangur/app/static/index.html` when UI implementation is authorized.
- Do not implement real client personalization, live Plaid, external APIs, or investment advice language without a specific authorized batch.

## Briefing Story Implementation Restart

- All UI Reporting / Briefing restart files.
- `src/arangur/workflow_templates.py`.
- `src/arangur/demo_pipeline.py`.
- `src/arangur/report_generator.py`.
- `tests/test_workflow_templates.py`.
- Existing synthetic report package examples under `reports/demo/`.
- Do not replace internal workflow contracts without preserving existing API compatibility.

## Manager-Role Review Restart

- All UI Reporting / Briefing restart files.
- `docs/ui_reporting/manager_role_review_v1.md`.
- `src/arangur/exposure_overlap.py`.
- `src/arangur/scenarios.py`.
- `src/arangur/report_generator.py`.
- Current synthetic fixture data under `data/demo/`.
- Do not use real manager data, real mandates, or recommendation language.
