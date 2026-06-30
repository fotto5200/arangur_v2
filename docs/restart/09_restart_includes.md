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

## Simulation Kernel Restart

- All Codex implementation restart files.
- `docs/architecture/simulation_kernel_three_surface_model_v1.md`.
- `docs/contracts/simulation_kernel_contracts_v1.md`.
- `docs/contracts/synthetic_position_universe_contract_v1.md`.
- `docs/contracts/synthetic_market_state_contract_v1.md`.
- `docs/contracts/simplified_daily_valuation_contract_v1.md`.
- `docs/contracts/report_element_input_mapping_contract_v1.md`.
- `docs/decisions/0003_three_surface_simulation_kernel.md`.
- `docs/architecture/thin_demo_system_architecture.md`.
- `docs/contracts/canonical_portfolio_snapshot_contract.md`.
- `docs/contracts/report_element_template_catalog_contract.md`.
- `docs/ui_reporting/report_element_finder_composer_current_model_v1.md`.
- `docs/architecture/scenario_engine_roadmap.md`.
- `docs/architecture/data_availability_workstream.md`.
- `docs/contracts/data_coverage_result_contract.md`.
- `data/simulation/synthetic_position_universe_summary.json`.
- `data/simulation/synthetic_market_state_summary.json`.
- `data/simulation/simplified_valuation_summary.json`.
- `data/simulation/report_element_inputs/report_element_input_summary.json`.
- `src/arangur/simulation/`.
- `src/arangur/report_elements/input_mapping.py`.
- `tests/test_synthetic_position_universe.py`.
- `tests/test_synthetic_market_state.py`.
- `tests/test_simplified_daily_valuation.py`.
- `tests/test_report_element_input_mapping.py`.
- Do not include real client data, live Plaid, external APIs, credentials, vendor market data, or legacy MATLAB.

## Synthetic Data Generation Restart

- All Simulation Kernel restart files.
- `docs/contracts/demo_data_contract.md`.
- `docs/contracts/market_data_fixture_contract.md`.
- `docs/contracts/plaid_mock_ingestion_contract.md` only for source-neutral adapter context, not live Plaid behavior.
- `docs/contracts/synthetic_position_universe_contract_v1.md`.
- `docs/contracts/synthetic_market_state_contract_v1.md`.
- `docs/contracts/simplified_daily_valuation_contract_v1.md`.
- `data/simulation/synthetic_position_universe.json`.
- `data/simulation/synthetic_position_universe_summary.json`.
- `data/simulation/synthetic_market_state_history.json`.
- `data/simulation/synthetic_market_state_summary.json`.
- `data/simulation/synthetic_scenario_market_states.json`.
- `data/simulation/daily_position_valuation_history.json`.
- `data/simulation/daily_portfolio_valuation_history.json`.
- `data/simulation/value_change_package.json`.
- `data/simulation/scenario_revaluation_results.json`.
- `data/simulation/simplified_valuation_summary.json`.
- `data/simulation/report_element_inputs/portfolio_status.json`.
- `data/simulation/report_element_inputs/concentration_theme.json`.
- `data/simulation/report_element_inputs/concentration_sector_industry.json`.
- `data/simulation/report_element_inputs/scenario_impact_by_manager_ai_chip_selloff.json`.
- `data/simulation/report_element_inputs/cash_generation_summary.json`.
- `data/simulation/report_element_inputs/manager_comparison.json`.
- `data/simulation/report_element_inputs/data_confidence_note.json`.
- `data/simulation/report_element_inputs/report_element_input_summary.json`.
- `src/arangur/simulation/position_universe.py`.
- `src/arangur/simulation/synthetic_position_universe_generator.py`.
- `src/arangur/simulation/market_state.py`.
- `src/arangur/simulation/synthetic_market_state_generator.py`.
- `src/arangur/simulation/daily_valuation.py`.
- `src/arangur/simulation/simplified_daily_valuation_engine.py`.
- `src/arangur/report_elements/input_mapping.py`.
- `tests/test_synthetic_position_universe.py`.
- `tests/test_synthetic_market_state.py`.
- `tests/test_simplified_daily_valuation.py`.
- `tests/test_report_element_input_mapping.py`.
- Future synthetic fixtures under `data/demo/` when implementation is authorized.
- Future generator source files under `src/` when implementation is authorized.
- Future focused generator tests under `tests/` when implementation is authorized.
- Keep all managers, accounts, positions, transactions, marks, and history fully synthetic.

## Valuation Engine Abstraction Restart

- All Simulation Kernel restart files.
- `docs/contracts/analytics_outputs_contract.md`.
- `docs/contracts/report_package_contract.md`.
- `docs/contracts/data_coverage_result_contract.md`.
- `docs/contracts/synthetic_position_universe_contract_v1.md`.
- `docs/contracts/synthetic_market_state_contract_v1.md`.
- `docs/contracts/simplified_daily_valuation_contract_v1.md`.
- `data/simulation/synthetic_position_universe.json`.
- `data/simulation/synthetic_market_state_history.json`.
- `data/simulation/synthetic_scenario_market_states.json`.
- `data/simulation/daily_position_valuation_history.json`.
- `data/simulation/daily_portfolio_valuation_history.json`.
- `data/simulation/value_change_package.json`.
- `data/simulation/scenario_revaluation_results.json`.
- Current synthetic generated report package examples under `reports/demo/` if implementation is authorized.
- Future valuation replacement or deepening source files under `src/` when implementation is authorized.
- Future focused valuation replacement or deepening tests under `tests/` when implementation is authorized.
- Do not implement tax lots, settlement reconciliation, production fixed-income accounting, production private-market accounting, or production performance attribution unless a later batch explicitly authorizes it.

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
- `docs/ui_reporting/guided_briefing_builder_correction_v1.md`.
- `docs/ui_reporting/report_element_finder_composer_current_model_v1.md`.
- `docs/ui_reporting/briefing_set_builder_model_v1.md`.
- `docs/ui_reporting/briefing_set_report_view_model_v1.md`.
- `docs/ui_reporting/briefing_set_client_preview_model_v1.md`.
- `docs/ui_reporting/briefing_set_builder_implementation_brief_v1.md`.
- `docs/ui_reporting/client_briefing_page_model_v1.md`.
- `docs/ui_reporting/manager_role_review_v1.md`.
- `docs/demo/report_workflow_implications.md`.
- `docs/architecture/deployable_demo_app_architecture.md`.
- `src/arangur/app/static/index.html` when UI implementation is authorized.
- Do not implement real client personalization, live Plaid, external APIs, or investment advice language without a specific authorized batch.

## Report Element Finder / Composer Restart

- All UI Reporting / Briefing restart files.
- `docs/ui_reporting/report_element_finder_composer_current_model_v1.md`.
- `docs/contracts/report_element_template_catalog_contract.md`.
- `docs/restart/CURRENT_STATE.md`.
- `docs/restart/08_next_actions.md`.
- `README.md`.
- `src/arangur/app/static/index.html` when UI implementation is authorized.
- `src/arangur/report_elements/` when catalog implementation is authorized.
- `tests/test_app_health.py` and `tests/test_report_element_catalog.py` when implementation is authorized.
- Keep discovery separate from saved spec fields, keep configuration template-driven, and do not implement report generation, backend persistence, live Plaid, external APIs, real data, or investment advice language unless a later batch explicitly authorizes it.

## Report Element Input Mapping Restart

- All Simulation Kernel restart files.
- `docs/contracts/report_element_input_mapping_contract_v1.md`.
- `docs/contracts/report_element_template_catalog_contract.md`.
- `data/simulation/synthetic_position_universe.json`.
- `data/simulation/synthetic_market_state_history.json`.
- `data/simulation/synthetic_scenario_market_states.json`.
- `data/simulation/daily_position_valuation_history.json`.
- `data/simulation/daily_portfolio_valuation_history.json`.
- `data/simulation/value_change_package.json`.
- `data/simulation/scenario_revaluation_results.json`.
- `data/simulation/simplified_valuation_summary.json`.
- `data/simulation/report_element_inputs/`.
- `src/arangur/report_elements/catalog.py`.
- `src/arangur/report_elements/templates.json`.
- `src/arangur/report_elements/input_mapping.py`.
- `tests/test_report_element_catalog.py`.
- `tests/test_report_element_input_mapping.py`.
- Do not generate final reports, charts, browser UI, client briefings, backend persistence, live Plaid, external APIs, Docker/Postgres changes, or real data.

## Guided Builder Implementation Restart

- All UI Reporting / Briefing restart files.
- `docs/ui_reporting/guided_briefing_builder_correction_v1.md`.
- `docs/ui_reporting/briefing_set_builder_model_v1.md`.
- `docs/ui_reporting/briefing_set_builder_implementation_brief_v1.md`.
- `docs/ui_reporting/client_briefing_page_model_v1.md`.
- `src/arangur/app/static/index.html`.
- `src/arangur/app/routes.py`.
- `src/arangur/app/run_service.py`.
- `tests/test_app_health.py`.
- `tests/test_app_runs_api.py`.
- Do not show raw report links, JSON links, recent run history, or technical panels on the first screen.

## Briefing Set Builder Implementation Restart

- All UI Reporting / Briefing restart files.
- `docs/ui_reporting/briefing_set_builder_model_v1.md`.
- `docs/ui_reporting/briefing_set_report_view_model_v1.md`.
- `docs/ui_reporting/briefing_set_client_preview_model_v1.md`.
- `docs/ui_reporting/briefing_set_builder_implementation_brief_v1.md`.
- `docs/ui_reporting/guided_briefing_builder_correction_v1.md`.
- `src/arangur/app/static/index.html`.
- `src/arangur/app/routes.py`.
- `src/arangur/app/run_service.py`.
- `tests/test_app_health.py`.
- `tests/test_app_runs_api.py`.
- Keep the main path focused on shared context, ordered report views, and client preview; keep raw artifacts in the technical/admin appendix.

## Report View Model Restart

- All UI Reporting / Briefing restart files.
- `docs/ui_reporting/briefing_set_report_view_model_v1.md`.
- `docs/contracts/report_package_contract.md`.
- `src/arangur/workflow_templates.py` when implementation is authorized.
- `src/arangur/report_generator.py` when implementation is authorized.
- Current synthetic report package examples under `reports/demo/` if implementation is authorized.
- Do not turn every report view into a separate top-level workflow unless a later contract batch requires it.

## Client Preview Implementation Restart

- All Briefing Set Builder Implementation restart files.
- `docs/ui_reporting/briefing_set_client_preview_model_v1.md`.
- `docs/ui_reporting/client_briefing_page_model_v1.md`.
- `docs/ui_reporting/audience_depth_modes_v1.md`.
- Current generated synthetic report package examples under `reports/demo/` if implementation is authorized.
- Do not expose workflow IDs, JSON links, report package links, raw artifact lists, or technical appendix material on the client preview by default.

## Client Briefing Page Implementation Restart

- All Guided Builder Implementation restart files.
- `docs/ui_reporting/client_briefing_page_model_v1.md`.
- `docs/ui_reporting/briefing_story_model_v1.md`.
- `docs/ui_reporting/audience_depth_modes_v1.md`.
- Current generated synthetic report package examples under `reports/demo/` if implementation is authorized.
- Do not expose workflow IDs, JSON links, report package links, raw artifact lists, or technical appendix material on the client briefing page by default.

## Technical/Admin Appendix Restart

- All Deployable Demo App restart files.
- `docs/ui_reporting/guided_briefing_builder_correction_v1.md`.
- `docs/ui_reporting/client_briefing_page_model_v1.md`.
- `docs/architecture/deployable_demo_app_architecture.md`.
- `src/arangur/app/`.
- Existing generated report package examples under `reports/demo/`.
- Keep technical/admin artifact browsing separate from the main advisor guided builder and client briefing page.

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
