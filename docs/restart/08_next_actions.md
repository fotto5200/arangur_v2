# Next Actions

## Immediate Architecture / Simulation Kernel Batches

- Completed baseline: deterministic synthetic position universe generator with 74 synthetic positions across public, private, cash, manager-level, and opaque assets, six managers, accounts, sleeves, 90-day transaction/history traces, themes, data-quality flags, and human-review flags.
- Completed baseline: deterministic synthetic market/state-of-world generator with 91 calendar dates, 12 core drivers, 23 expanded required state variables, proxy mappings, confidence flags, historical paths, five scenario market states, and a covariance recovery check. This batch intentionally does not generate position values, portfolio values, value-change packages, reports, or charts.
- Completed baseline: deterministic simplified daily valuation engine with 91 daily portfolio valuations, 6,734 position valuations, value-change package, scenario revaluation results for five scenarios, confidence summaries, human-review values, and validation. This batch intentionally does not connect UI or report generation.
- Completed baseline: report-element input mapping layer that consumes the synthetic simulation outputs and writes structured inputs for Portfolio Status, Concentration, Scenario Impact by Manager, Cash Generation Summary, Manager Comparison, and Data Confidence Note. This batch intentionally does not generate final reports, charts, browser UI, persistence, live data, or external API calls.
- Completed baseline: report-element rendering layer that consumes report-element input payloads and writes simple deterministic view JSON plus Markdown/HTML fragments for the initial Portfolio Status, Concentration, Scenario Impact by Manager, Cash Generation Summary, Manager Comparison, and Data Confidence Note elements. This batch intentionally does not generate full client briefings, charts, browser UI integration, persistence, live data, or external API calls.
- Completed baseline: briefing-set preview assembly layer that consumes rendered report-element views and writes deterministic Client Briefing Set and Advisor Review Set preview JSON, Markdown, HTML, and static index fixtures. This batch intentionally does not integrate the browser UI, generate charts, persist briefing sets, call workflow APIs, use live data, or create production client-ready report packages.
- Completed baseline: browser composer preview linkage that safely serves committed `data/simulation` artifacts under `/simulation`, matches local analytic specs to existing rendered views, opens matching one-element HTML previews, and keeps QA reference preview links available outside the main advisor path. This batch intentionally does not generate reports from local specs, persist specs, call workflow APIs from the composer, add charts, or use live data.
- Completed baseline: local browser spec-set export/restore and current-set preview. The composer can copy/download schema `arangur.local_briefing_spec_set.v1`, restore it locally, and preview the current unsaved Client Briefing Set or Advisor Review Set using existing rendered views plus placeholders. This batch intentionally does not persist specs, generate reports, call workflow APIs from the composer, add charts, or use live data.
- Completed baseline: backend-free print/export formatting for the current local preview. After a non-empty current Client Briefing Set or Advisor Review Set preview is opened, the browser can print the selected preview, download standalone local HTML, or copy plain preview text. This batch intentionally does not persist specs, generate server-side reports, call workflow APIs from the composer, add charts, or use live data.
- Completed baseline: local preview/export UX polish. The browser-local composer now keeps technical local export details collapsed and labeled as technical, blocks empty spec-set copy/download with helpful messages, reports restored Client/Advisor spec counts, gives the current preview more breathing room, distinguishes client-facing from advisor/internal preview purpose, and keeps print/export controls visually secondary. This batch intentionally does not persist specs, generate server-side reports, call workflow APIs from the composer, add charts, or use live data.
- Completed baseline: browser-demo readiness QA polish for the local composer/preview/export flow. The browser-local surface keeps the main advisor path sparse, keeps technical JSON details secondary/collapsed, uses clearer local set JSON copy/download/restore language, preserves preview/print/export controls, and still avoids `/api/runs` from the composer.
- Completed baseline: backend briefing spec-set persistence API. The app validates the browser-local spec-set payload, returns a clear not-configured response in `DB_ENGINE=none`, creates optional Postgres `briefing_spec_set` and `briefing_spec_item` tables when configured, and exposes secondary browser save/load controls without removing local export/restore or calling `/api/runs`.
- Completed baseline: advisor-facing preview flow cleanup. The browser composer keeps the main flow as build -> preview -> edit, blocks empty-set preview with clear client/advisor prompts, opens a focused Preview Client Briefing or Preview Advisor Review surface for non-empty sets, hides the builder while previewing, exposes only Back to Builder, Print, Export HTML, Copy text, and a compact demo caveat there, moves local JSON transfer, backend draft save/load, and QA reference previews into Advanced, and uses nontechnical not-previewable guidance/placeholders. This batch intentionally does not change finder/template catalog behavior, backend persistence, endpoints, Docker/Postgres, generated reports, dependencies, analytics, simulation, live data, or external APIs.
- Completed baseline: browser visual QA and small polish for the cleaned advisor preview flow. The focused preview now keeps Back to Builder and preview export actions near the preview title, Advanced copy is less developer-facing, QA reference previews stay out of the main path, and unsupported-element guidance is advisor-facing. This batch intentionally does not change finder/template catalog behavior, backend persistence, endpoints, Docker/Postgres, generated reports, dependencies, analytics, simulation, live data, or external APIs.
- Completed baseline: advisor workflow shell and dependent configuration. The browser composer now starts on Advisor Home, routes Home/Builder/Preview/Advanced through static hash routes so browser Back stays within the workflow, and adds required manager/account/sleeve/strategy selectors when a selected scope is chosen. Selected entities are stored in local spec parameters and appear in advisor-facing row and preview labels. Advanced local export/restore, backend draft save/load, and QA reference previews remain secondary. This batch intentionally does not add backend routes, persistence behavior, Docker/Postgres changes, generated reports, dependencies, analytics, simulation, live data, or external APIs.
- Completed baseline: named workflow home and preview scope guards. Advisor Home now organizes product-level workflow steps as Design / Edit, Populate, Present, Named saved workflows, and Developer / QA tools; the Builder can name, save, open, copy, and delete browser-local saved workflow drafts using `localStorage`; Advanced has been demoted and relabeled as Developer / QA tools; and demo-rendered elements guard selected-scope previews when no committed selected-scope fixture exists. This batch intentionally does not add backend schema changes, generated report history, report generation from saved workflows, Docker/Postgres changes, dependencies, analytics, simulation, live data, or external APIs.
- Completed baseline: simplified Advisor Home and report scope choices. Advisor Home now has exactly four top-level product choices: Create a new workflow, Work with an existing workflow, Populate a workflow with data, and Present / view reports. Create reveals client/advisor workflow type choices; Work with existing is the single open/copy/delete saved-workflow surface; Populate and Present are staged until generated report workflows exist; Developer / QA remains secondary; and preview scope choices no longer imply unsupported duplicate selected-scope or all-managers cash behavior. This batch intentionally does not add backend routes, schema changes, generated report history, report generation from saved workflows, Docker/Postgres changes, dependencies, analytics, simulation, live data, or external APIs.
- Completed baseline: workflow naming and action modes. Browser-local saved workflow records now keep readable `display_name` values separately from internal `workflow_id` / `storage_key`, copies keep readable names, legacy id/name records still load through a compatibility layer, and the saved-workflow chooser separates edit, Populate with current demo data, and Present / view reports into distinct routes and screens. Populate remains a local demo populated preview only, Present uses the existing browser preview renderer without builder/finder/JSON/backend controls, and no backend routes, generated report history, Docker/Postgres changes, dependencies, analytics, live data, or external APIs were added.
- Completed baseline: saved workflow identity and naming. Browser-local workflow records now preserve readable names such as `Report Number 2`, keep `workflow_id` separate from `display_name`, carry local created/updated timestamps plus a simple workflow type label, and expose distinct Save, Rename, Save As New, and Copy behavior. Save updates the current workflow id without renaming it, Rename changes the display name for the same id and blocks duplicate names, Save As New creates a separate id without removing the original, Copy uses a readable copy name and leaves the source workflow listed, and legacy id/name records still load without destructive migration. This batch intentionally does not add backend routes, backend schema changes, generated report history, Docker/Postgres changes, dependencies, analytics, live data, or external APIs.
- Completed baseline: local Docker private-demo stack and runtime smoke. `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.env.private-demo.example`, and `docs/deployment/private_demo_docker.md` now package the FastAPI app with an internal Postgres service, demo-only env-file configuration, `/api/health` smoke checks, safe startup schema initialization through existing `CREATE TABLE IF NOT EXISTS` statements, and packaging tests. Frank verified on 2026-07-02 that the local app and Postgres came up with Compose, `/api/health` returned `status: ok` with `app_env: private_demo`, `runtime_mode: private_demo`, `db_engine: postgres`, and `database_configured: true`, `/app/` loaded, and a Postgres-backed briefing spec-set POST/list smoke worked. This remains local/private-demo only and intentionally does not deploy publicly, configure Caddy/Lightsail/Cloudflare/DNS, add production auth, add real secrets, use real data, add generated report history, redesign the UI, or require Docker/Postgres for normal local tests.
- Completed baseline: local private-demo preflight smoke helpers. `scripts\private_demo_smoke.cmd` now assumes the Docker stack is running and uses `curl.exe` only to check `/api/health`, `/app/`, `/api/report-elements`, briefing spec-set POST, and briefing spec-set list. `scripts\fixtures\private_demo_seed_briefing_spec_set.json` provides a synthetic/demo-only payload with one Client Briefing Set item and one Advisor Review Set item. `scripts\private_demo_down.cmd` stops the stack and requires an explicit `--reset` plus confirmation before deleting the local Postgres volume. This batch intentionally does not change app behavior, require Docker in tests, add production auth, add real secrets, use real data, add generated report history, deploy publicly, or configure Caddy/Lightsail/Cloudflare/DNS.
- Completed baseline: generated report artifact model. `src/arangur/report_elements/generated_report_artifact.py` defines and validates deterministic synthetic generated report artifacts with report metadata, source workflow fields, dated data snapshot fields, ordered sections, unsupported/caveat sections, `demo_partial` render status, text content, HTML content, summary metadata, and a scratch writer. It assembles one client briefing artifact and one advisor review artifact from existing briefing-set preview fixtures without changing UI, app routes, persistence schema, Docker, deployment, analytics, simulation, real data, or external APIs. `docs/contracts/generated_report_artifact_contract_v1.md` records the workflow -> preview -> generated artifact -> presentation distinction and states that generated artifacts are product objects, not a reason to add debugging panels to the advisor path.
- Completed baseline: demo workflow population to report artifacts. `src/arangur/app/generated_reports.py` validates browser-local saved workflow payloads, maps Client Briefing or Advisor Review specs to existing synthetic rendered views plus clean placeholders, and returns an ephemeral `generated_report_artifact.v1` through `POST /api/generated-reports/demo-populate`. The Populate workflow now lets an advisor choose a saved workflow, use `Current synthetic demo snapshot` / `2026-06-30`, create a demo populated report, and open a clean artifact view with advisor-authored workflow sections, concise metadata/caveat footer, Back to Home, Back to Workflow, Print, Export HTML, and Copy text. This batch intentionally does not add a report library, generated report history, backend schema, Docker/deployment changes, new analytics, simulation changes, live data, real client data, external APIs, or dependencies.
- Completed baseline: private-demo walkthrough and QA checklist. `docs/demo/private_demo_walkthrough.md` gives Frank or another demo operator a concise Windows-cmd flow for starting the local Docker stack, running `scripts\private_demo_smoke.cmd`, opening Advisor Home, creating a named Client Briefing Workflow, populating it with `Current synthetic demo snapshot`, opening the generated report, returning to `Present / view reports`, confirming Print / Export HTML / Copy text, and stopping the stack. It also records pass/fail checks for infrastructure, Home/workflow, Builder, Populate, Present, content quality, and current limitations. This batch intentionally does not add product features, UI controls, backend generated report persistence, Docker services, deployment changes, production auth, real data, external APIs, or dependencies.
- Completed baseline: generated report workflow identity fix. Populate now treats the selected browser-local saved workflow id as source of truth, resolves the saved payload by `workflow_id` at create time, blocks calmly when the saved workflow is missing, and no longer builds generated-report requests from stale current builder state. The Populate view shows a concise source-workflow confirmation, generated report titles derive from the selected workflow display name, malformed old generated-report shelf records are skipped, and repeated Populate actions get distinct `report_id` values so the browser-local shelf stores by artifact id without unintended overwrite. This batch intentionally does not add product features, new advisor controls, report library/history, backend persistence, Docker/deployment changes, production auth, real data, external APIs, or dependencies.
- Completed baseline: generated report preview alignment. Commit `524a99b` makes generated report body sections preserve the selected advisor-authored workflow sequence, selected template titles, authored narrative text, and matched Preview detail; automatic framing/closing sections are no longer inserted.
- Completed checkpoint: Frank manually reran the local private-demo browser rehearsal after commit `524a99b`. Docker stack startup, smoke script, authored workflow preview, copied-workflow Populate, generated report sequence, absence of automatic framing/closing sections, and Present / view reports opening all passed. The Docker/private-demo stack remains local only.
- Completed baseline: Arranger analytic control-plane boundary and first analytic pack contract. `docs/architecture/arranger_control_plane_boundary_v1.md` defines the internal Arranger control plane -> approved analytic pack -> Arangur consumption boundary; `docs/contracts/analytic_pack_contract_v1.md` defines the first pack components; `data/analytic_packs/arranger_demo_pack_v1/` contains a minimal synthetic fixture skeleton; and `tests/test_analytic_pack_contract.py` validates shape, id uniqueness, scenario shock references, report-element id compatibility, synthetic-demo marking, and the internal/not-advisor-facing publish-consume boundary. This batch intentionally does not add advisor UI, Arranger Studio UI, backend endpoints, deployment docs/config, Docker changes, simulation changes, scenario math, live data, external APIs, real data, dependencies, or pushes.
- Completed baseline: Published and applied the first Arranger Demo Analytic Pack v1. The fixture pack now has 12 curated themes, 4 lenses, 5 supported synthetic scenarios, matching shocks, 6 data confidence rules, and capability coverage for all current report element ids. `src/arangur/analytics/analytic_pack_loader.py` provides a standard-library loader/validator, and `src/arangur/analytics/apply_demo_pack.py` writes deterministic proof outputs under `data/simulation/analytics/`: theme exposure, manager/theme overlap, scenario impact by theme/manager, data confidence map, cross-scenario resilience, and an output index. This batch intentionally does not add advisor UI, Arranger Studio UI, backend endpoints, deployment docs/config, Docker changes, report-element input mapping, generated-report wiring, simulation-kernel changes, scenario engine math, live data, external APIs, real data, dependencies, or pushes.
- Completed baseline: Mapped analytic proof outputs into current report-element inputs and renderer views. `src/arangur/report_elements/analytic_input_mapping.py` writes separate analytic payloads for Concentration, Manager Comparison, Scenario Impact by Manager, Data Confidence Note, and Portfolio Status under `data/simulation/report_element_inputs/`; the renderer writes corresponding view JSON, Markdown, HTML, and `report_element_analytic_view_summary.json` under `data/simulation/report_element_views/`. This batch intentionally does not add advisor UI, generated-report wiring, backend endpoints, Docker/deployment changes, charts, live data, external APIs, real data, dependencies, or pushes.
- Completed baseline: Analytic-derived rendered views are now wired into the existing Advisor workflow path. The Builder exposes curated Arranger Demo Analytic Pack choices for supported templates, Preview and Populate can resolve supported configured specs to analytic fragments, Present opens the same generated report sections from the browser-local shelf, and unsupported combinations remain clean placeholders. This batch intentionally does not add Arranger Studio UI, control-plane editor surfaces, new Advisor Home choices, backend endpoints, Docker/deployment changes, live data, external APIs, real data, dependencies, or pushes.
- Completed baseline: Analytic Report Demonstration Pack v1. The analytic report fragments now include concise advisor takeaways and restrained caveats for Portfolio Status, Concentration, Manager Comparison, Scenario Impact, and Data Confidence; the local demo story is documented at `docs/demo/analytic_report_demo_story_v1.md`; and `docs/demo/analytic_demo_workflow_fixture.json` provides a restoreable browser-local workflow that exercises the supported analytic elements in Client Briefing and Advisor Review order. This batch intentionally does not add Arranger Studio UI, control-plane UI, new Advisor Home choices, dashboards, backend endpoints, Docker/deployment changes, live data, external APIs, real data, dependencies, or pushes.
- Completed architecture checkpoint: Arranger Internal Analytics Algorithm Design v1, revised around full portfolio revaluation. `docs/architecture/arranger_internal_analytics_algorithm_design_v1.md` now makes base market state valuation versus scenario market state valuation the only scenario impact methodology; key-rate/driver perturbations only construct complete scenario market states; themes classify and attribute impacts after valuation; and coverage/confidence records describe revaluation limitations. This batch intentionally does not add production code, advisor UI, Arranger Studio UI, backend endpoints, Docker/deployment changes, scenario-engine runtime, covariance/PCA runtime, live data, external APIs, real data, dependencies, or pushes.
- Completed architecture checkpoint: Key Market-State Scenario Basis Design v1. `docs/architecture/key_market_state_scenario_basis_design_v1.md` defines scenario basis models as small, curated, price-like coordinate systems for constructing complete scenario market states, with multiple possible approved basis models, deterministic and reduced covariance/PCA completion methods, expansion rules, validation layers, and a hard boundary before full portfolio revaluation. This batch intentionally does not add production code, advisor UI, report views, generated analytics outputs, backend endpoints, Docker/deployment docs, live data, external APIs, real data, dependencies, or pushes.
- Completed architecture checkpoint: Thesis Lens Position Mapping Design v1. `docs/architecture/thesis_lens_position_mapping_design_v1.md` defines complete thesis-specific position mapping schemas, deterministic classification precedence, internal LLM-assisted classification policy, published mapping artifacts, and post-valuation thesis aggregation boundaries. This batch intentionally does not add production code, advisor UI, report views, generated analytics outputs, backend endpoints, Docker/deployment docs, live data, external APIs, real data, dependencies, or pushes.
- Completed architecture checkpoint: Position Valuation Coverage Mapping Design v1. `docs/architecture/position_valuation_coverage_mapping_design_v1.md` defines the position -> instrument -> pricing function -> required market input -> valuation result -> coverage status path used by the full revaluation skeleton. This batch intentionally does not add production code, advisor UI, report views, generated analytics outputs, backend endpoints, Docker/deployment docs, live data, external APIs, real data, dependencies, or pushes.
- Completed baseline: Synthetic Full Revaluation Engine Skeleton v1. `src/arangur/analytics/pricing_functions.py`, `src/arangur/analytics/revaluation.py`, and `src/arangur/analytics/revaluation_runner.py` generate deterministic internal fixtures under `data/simulation/revaluation/`: instrument catalog, position catalog, pricing-function registry, base/scenario market states, position-pricing assignments, base/scenario coverage maps, base/scenario position valuation results, position value comparisons, portfolio revaluation summary, valuation coverage manifest, and revaluation bundle manifest for `ai_chip_selloff`. This batch intentionally does not add advisor UI, report views, backend endpoints, Docker/deployment changes, live market data, external APIs, real data, production pricing, covariance/PCA runtime, dependencies, or pushes.
- Next ask Frank/ChatGPT which internal/local product path to take next: broaden the revaluation skeleton across more scenarios or instrument treatment, map the revaluation bundle into analytic/report-element input fixtures, improve specific report-content elements, or begin thesis-lens aggregation on top of revalued position impacts. Keep additional advisor UI/report-consumption expansion paused until that decision is explicit. Keep private-server deployment planning parked, and keep local UI micro-polish parked unless a blocking rehearsal issue appears. Do not implement charts, live data, production auth, production reporting, generated report history, full report library UI, Caddy, Lightsail, Cloudflare, DNS, or public deployment changes unless explicitly authorized.
- Later add durable server-side report generation from saved Client Briefing Set and Advisor Review Set specs only after product requirements remain stable.

## Batch 2: Architecture And Contracts For Thin Demo

- Goal: Expand architecture and contract docs enough to guide implementation.
- Mode: Documentation and schema-design batch.
- Allowed scope: `docs/architecture/`, `docs/contracts/`, `docs/demo/`, `docs/restart/`, and lightweight README pointers.
- Non-goals: No Plaid, no MATLAB audit, no real client data, no production UI.
- Acceptance criteria: Thin-demo components have clear inputs, outputs, invariants, fixture expectations, demo storyline, and dataset plan.
- Stop conditions: Existing substantial docs would be overwritten, secrets/client data appear necessary, or MATLAB inspection appears required.

## Batch 3: Local Demo Vertical Slice

- Goal: Implement local demo data loader -> canonical snapshot -> valuation/exposure/scenario outputs -> generated Markdown report.
- Mode: Implementation batch.
- Allowed scope: `data/demo/`, `reports/demo/`, `src/`, `tests/`, `docs/contracts/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No Plaid, no live APIs, no deep valuation, no MATLAB audit, no production UI.
- Acceptance criteria: Synthetic JSON fixtures load deterministically; a canonical snapshot is produced; market data prices every held non-cash security; valuation, exposure/overlap, and scenario outputs reconcile; a Markdown report is generated under `reports/demo/`; focused tests or deterministic checks pass.
- Stop conditions: Real data is encountered, schemas require unresolved product judgment, external APIs or credentials appear necessary, or implementation needs new dependencies without clear justification.

## Batch 4: Refine Report Quality And Demo Outputs

- Goal: Improve the generated advisor-readable Markdown report and optionally add a simple static HTML output from the same report package.
- Mode: Implementation and documentation batch.
- Allowed scope: `src/`, `tests/`, `reports/demo/`, `docs/demo/`, `docs/contracts/`, and `docs/restart/`.
- Non-goals: No production UI, no Plaid, no live APIs, no real client data, no advisor assistant.
- Acceptance criteria: Report sections are clearer, tables are consistently formatted, Markdown and simple HTML outputs are generated, caveats remain prominent, validation errors are clearer, and focused tests cover report generation and malformed local fixtures.
- Stop conditions: Report claims could be confused with real advice, generated outputs require client data, or layout tooling becomes a dependency decision.

## Batch 5: Plaid-Shaped Mock Ingestion Adapter

- Goal: Add a mock adapter that looks like Plaid ingestion but uses local synthetic Plaid-shaped fixtures.
- Mode: Implementation batch.
- Allowed scope: `data/demo/`, `src/`, `tests/`, `docs/contracts/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No Plaid Sandbox, no live Plaid credentials, no external API calls.
- Acceptance criteria: Mock Plaid-shaped input produces the same canonical snapshot type as the demo data loader and existing analytics/report outputs can run from that snapshot.
- Stop conditions: Live credentials appear necessary, external API access is required, or canonical snapshot gaps need product-owner decisions.

## Batch 6: Lightweight Local Report Index / Viewer

- Goal: Add a simple local report index or non-interactive viewer entry point for generated demo outputs.
- Mode: Implementation or design spike.
- Allowed scope: `src/`, `reports/demo/`, `docs/demo/`, `tests/`, and `docs/restart/`.
- Non-goals: No production dashboard, no live APIs, no credentials, no real client data.
- Acceptance criteria: Implemented baseline: a colleague can find and open generated Markdown/HTML/JSON outputs from a simple local entry point.
- Stop conditions: UI scope becomes broad, dependencies become necessary, or product direction is unclear.

## Batch 7: Harden Analytics And Validation

- Goal: Harden deterministic valuation, exposure/overlap summaries, scenario shocks, validations, and edge-case handling after the first vertical slice exists.
- Mode: Implementation batch.
- Allowed scope: `src/`, `tests/`, `data/demo/`, `docs/contracts/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No vendor data, no full accounting, no advanced risk model, no Plaid.
- Acceptance criteria: Calculations have stronger validation, clearer errors, and tests for missing prices, duplicated IDs, cash, and scenario rule precedence.
- Stop conditions: Missing vertical slice, unresolved scenario methodology decision, or unsafe source data.

## Batch 8: Plaid Sandbox Integration Design

- Goal: Design the future Plaid Sandbox integration and operational boundaries.
- Mode: Design batch, possibly followed by implementation only if authorized.
- Allowed scope: `docs/architecture/`, `docs/contracts/`, `docs/decisions/`, `docs/restart/`, and possibly `src/` stubs if explicitly authorized.
- Non-goals: No live Plaid production access, no private credentials committed, no real client ingestion.
- Acceptance criteria: Sandbox flow, secrets policy, adapter contract, and test strategy are documented, building on the existing Plaid-shaped mock adapter.
- Stop conditions: Credentials or account setup are required, strategy needs Frank, or implementation scope exceeds the design batch.

## Batch 9: Workflow Simulation Templates

- Goal: Add lightweight workflow simulation templates for quarterly review, manager overlap review, scenario risk review, intake review, and data coverage review.
- Mode: Implementation batch.
- Allowed scope: `src/`, `tests/`, `reports/demo/`, `docs/demo/`, `docs/restart/`, and small synthetic metadata fixtures under `data/demo/` if useful.
- Non-goals: No advisor assistant, no interactive app, no live APIs, no credentials, no real client data.
- Acceptance criteria: Implemented baseline: each workflow type has a simple local template, report packages identify the selected workflow clearly, generated Markdown/HTML reports include workflow-specific framing, and tests verify workflow-specific output metadata. Use `docs/demo/report_workflow_implications.md` as design input for future refinement.
- Stop conditions: Workflow design requires Frank's product judgment, UI scope expands, or real advisor/client data appears necessary.

## Batch 10: Data Coverage / Valuation Confidence Report Prototype

- Goal: Prototype a synthetic Data Coverage / Valuation Confidence report family that explains source coverage, missing data, stale values, valuation method, and human-review needs.
- Mode: Implemented baseline; future batches can deepen source inventory and reconciliation.
- Allowed scope: `data/demo/`, `src/`, `tests/`, `reports/demo/`, `docs/demo/`, `docs/contracts/`, and `docs/restart/`.
- Non-goals: No real client data, no vendor ingestion, no document extraction, no automated private asset valuation, no forecasting.
- Acceptance criteria: Implemented baseline: each pipeline run writes `data_coverage_result.json`, report packages expose coverage summaries and human-review counts, generated reports include a Data Coverage and Valuation Confidence section, the static index shows data confidence information, and focused tests verify deterministic output.
- Stop conditions: Real data appears necessary, vendor selection is required, confidence scoring needs Frank's product decision, or implementation drifts into market-data ingestion.

## Batch 11: Scenario Library / Source Model Design

- Goal: Design a source-normalized scenario library layer that can represent hand-authored scenarios, advisor templates, firm assumptions, and future external scenario sources.
- Mode: Design batch.
- Allowed scope: `docs/architecture/`, `docs/contracts/`, `docs/demo/`, `docs/restart/`, and `docs/decisions/`.
- Non-goals: No stochastic simulation, no live external data sources, no licensed scenario-source integration, no UI.
- Acceptance criteria: Scenario source metadata, scenario versioning, narrative-to-assumption mapping, and report caveats are documented.
- Stop conditions: External research or vendor choice is required, licensing questions need Frank, or implementation is requested before the contract is clear.

## Batch 12: Later Stochastic Scenario Prototype

- Goal: Prototype reproducible covariance/random-number-driven scenario ranges after deterministic scenario outputs and scenario source modeling are stable.
- Mode: Future implementation spike only after authorization.
- Allowed scope: To be defined later; likely `src/`, `tests/`, `data/demo/`, `docs/contracts/`, and `reports/demo/` with synthetic fixtures only.
- Non-goals: No production risk model, no market prediction claims, no live market-data ingestion, no external APIs, no real client data.
- Acceptance criteria: A synthetic covariance/driver fixture produces reproducible seeded impact ranges with clear caveats and no forecasting language.
- Stop conditions: Methodology is not approved, covariance data source is unclear, external data is required, or report language risks implying forecasts.

## Batch 13: FastAPI App Shell And Health Endpoint

- Goal: Add the first deployable app shell using FastAPI and `uvicorn`, with a health endpoint and private-demo settings boundary.
- Mode: Implemented baseline.
- Allowed scope: `src/`, `tests/`, `docs/`, and lightweight README updates.
- Non-goals: No Docker yet, no Postgres schema yet, no browser UI beyond a placeholder if needed, no live Plaid, no real data.
- Acceptance criteria: Implemented baseline: app can be imported and started with `uvicorn`, `GET /api/health` returns a minimal status payload, settings include `APP_ENV=private_demo` concepts without committing secrets, a static placeholder console is served, and tests cover health/settings/page behavior.
- Stop conditions: Dependencies, app layout, or environment handling requires product/ops decisions beyond the Education-stack pattern.

## Batch 14: API Endpoints Wrapping Existing Pipeline Runs

- Goal: Add API endpoints that expose supported sources/workflows and run the existing synthetic pipeline through service wrappers.
- Mode: Implemented baseline.
- Allowed scope: `src/`, `tests/`, `docs/`, and generated local demo artifacts only if endpoint tests intentionally regenerate them.
- Non-goals: No database persistence yet unless Batch 15 is already complete, no live Plaid, no external APIs, no real data.
- Acceptance criteria: Implemented baseline: `/api/sources`, `/api/workflows`, `/api/runs`, `/api/runs/{run_id}`, `/api/reports/index`, and `/reports/demo/...` static artifact serving are file-backed, validate source/workflow choices, call the existing pipeline modules without duplicating analytics, and return run/artifact summaries with synthetic-data flags.
- Stop conditions: Background job infrastructure becomes necessary, endpoint protection strategy is required before the next private-demo step, or code changes would bypass current pipeline contracts.

## Batch 15: Postgres Persistence Skeleton

- Goal: Implement the first Postgres-backed persistence skeleton for workflow runs, artifact records, data coverage summaries, and optional run events.
- Mode: Implemented baseline.
- Allowed scope: `src/`, `tests/`, `docs/`, and migration/schema files if the project adds a migration folder.
- Non-goals: No real client data model, no full portfolio relational decomposition, no production auth, no managed database service.
- Acceptance criteria: Implemented baseline: `src/arangur/app/persistence.py` defines optional Postgres schema initialization for `workflow_run`, `report_artifact`, and `run_event`, maps current run summaries into persistence records, leaves `DB_ENGINE=none` as the no-database local default, and keeps JSON artifacts as the source of detailed output.
- Stop conditions: Migration tool choice requires a dependency decision not already authorized, tests require live Postgres outside a Docker smoke batch, or persistence design expands into production account/holding modeling.

## Batch 16: Browser UI Shell

- Goal: Add a simple browser UI served by the backend for source/workflow selection, run workflow, run history, report links, and data confidence summary.
- Mode: Implemented baseline.
- Allowed scope: `src/`, `tests/`, `docs/`, and simple static assets if used.
- Non-goals: No separate frontend framework unless explicitly authorized, no production dashboard, no client data upload, no rich charting.
- Acceptance criteria: Implemented baseline: `/`, `/app/`, and `/app/index.html` serve a dependency-free static console with source selector, workflow selector, run button, latest run summary, run history/list, report links, data confidence summary, and synthetic-data caveat. The page calls the existing file-backed API and does not introduce a frontend framework.
- Stop conditions: UI scope expands into advisor assistant, production dashboard, production authentication, or design-system work that needs product review.

## Batch 16A: Client-Question Briefing Console Redesign

- Goal: Redesign the browser demo console around client question, audience depth, and briefing preparation while keeping existing workflow APIs behind the scenes.
- Mode: Implemented baseline.
- Allowed scope: `src/arangur/app/`, `tests/`, `docs/restart/`, `docs/ui_reporting/`, and README pointers.
- Non-goals: No frontend framework, no production dashboard, no real client data, no live Plaid, no production authentication.
- Acceptance criteria: Implemented transitional baseline: first screen starts with `Client question`; audience depth defaults to `Standard Family Office Meeting`; source is secondary; workflow mapping is internal; prepared briefing shows plain-English "what to look at" guidance, key evidence, data confidence/caveats, report links, drill-down artifacts, technical details, and recent briefings.
- Stop conditions: UI scope expands into production client portal, advisor autonomy/AI claims need product review, or report language risks investment advice.

## Batch 16A-1: Guided Briefing Builder Correction

- Goal: Capture the correction that the target UI is a sparse guided briefing builder, not a dense briefing console.
- Mode: Implemented documentation baseline.
- Allowed scope: `docs/ui_reporting/`, `docs/architecture/`, `docs/restart/`, `docs/decisions/`, `docs/demo/`, and README pointers.
- Non-goals: No code changes, no generated reports, no tests, no frontend framework.
- Acceptance criteria: Implemented baseline: `docs/ui_reporting/guided_briefing_builder_correction_v1.md` and `docs/ui_reporting/client_briefing_page_model_v1.md` define the guided-builder sequence, client briefing page, layer model, first-screen exclusions, and technical/admin appendix boundary.
- Stop conditions: Product direction conflicts require Frank or ChatGPT strategic review.

## Batch 16A-2: Sparse Guided Briefing Builder Implementation

- Goal: Replace the dense one-page briefing console with a stepwise builder that shows one clear choice at a time.
- Mode: Implemented baseline.
- Allowed scope: `src/arangur/app/`, `tests/`, `docs/restart/`, `docs/ui_reporting/`, and README pointers.
- Non-goals: No frontend framework, no production client portal, no real client data, no live Plaid, no backend persistence refactor unless a tiny compatibility field is necessary.
- Acceptance criteria: Implemented baseline: first screen shows only purpose, compact synthetic/local caveat, four required client-question cards, and a small technical/admin entry; audience depth, portfolio context, briefing bundle, advisor draft, and client briefing open in later steps; prior choices collapse into a compact summary; raw report links, JSON links, run history, and technical panels are absent from the first screen.
- Stop conditions: Implementation requires a frontend framework, production auth, real data, or major backend/report-generator changes.

## Batch 16A-3: Client Briefing Page Surface

- Goal: Add a separate answer-first client briefing page generated from the guided builder selection.
- Mode: Implemented static baseline; recommended refinement batch for persisted/generated report behavior.
- Allowed scope: `src/arangur/app/`, `src/arangur/` only for small report metadata helpers if needed, `tests/`, `docs/ui_reporting/`, and README pointers.
- Non-goals: No production client portal, no real client data, no investment recommendation engine, no full PDF/export workflow.
- Acceptance criteria: Static baseline implemented in the browser app: client briefing view shows demo title, client question, plain-English answer, selected cards, compact confidence note, and optional evidence/advisor/technical appendix controls; workflow IDs, JSON links, report package links, raw artifact lists, and technical/admin details are hidden by default. Future refinement should persist/export this briefing more cleanly.
- Stop conditions: Client-facing language requires product/legal review beyond existing demo caveats.

## Batch 16A-4: Advisor Draft Step

- Goal: Add an advisor review step between suggested briefing bundle and client briefing.
- Mode: Implemented static baseline; recommended refinement batch if richer advisor draft behavior is needed.
- Allowed scope: `docs/ui_reporting/`, `src/arangur/app/`, `tests/`, and small report metadata helpers if needed.
- Non-goals: No AI advisor chat, no autonomous investment advice, no real client personalization.
- Acceptance criteria: Static baseline implemented in the browser app: advisor sees question, draft answer, selected cards, confidence summary, and buttons for client briefing, evidence appendix, advisor notes, technical/admin details, and start over.
- Stop conditions: Drafting behavior requires LLM integration, real client history, or compliance/product decisions.

## Batch 16A-5: Technical/Admin Appendix

- Goal: Move technical links, report package JSON, local report index, run history, source adapters, workflow IDs, and artifact paths out of the main guided path into a clearly labeled technical/admin appendix.
- Mode: Implemented static baseline; recommended refinement batch for protected/admin routing later.
- Allowed scope: `src/arangur/app/`, `tests/`, docs, and existing static app assets.
- Non-goals: No production admin console, no new auth system unless part of a later private-demo protection batch.
- Acceptance criteria: Static baseline implemented in the browser app: main builder and client briefing are free of raw technical artifacts by default; technical/admin appendix preserves validation and report-browser access for developers/advisors after interaction.
- Stop conditions: Protected admin/report surface policy requires Frank decision before implementation.

## Batch 16A-6: Briefing Set Builder Model

- Goal: Capture the correction that the target UI is a Briefing Set Builder, not a one-report guided wizard.
- Mode: Implemented documentation baseline.
- Allowed scope: `docs/ui_reporting/`, `docs/architecture/`, `docs/restart/`, `docs/decisions/`, `docs/demo/`, and README pointers.
- Non-goals: No code changes, no generated reports, no tests, no dependencies, no Docker/Postgres changes.
- Acceptance criteria: Implemented baseline: briefing set model, report view model, client preview model, and next UI implementation brief define shared context, ordered report views, client preview, technical/admin appendix boundaries, and acceptance criteria for the next UI batch.
- Stop conditions: Product direction conflicts require Frank or ChatGPT strategic review.

## Batch 16A-7: Briefing Set Builder UI

- Goal: Transform the current sparse guided builder into a Briefing Set Builder.
- Mode: Superseded local UI baseline.
- Allowed scope: `src/arangur/app/`, tests, `docs/ui_reporting/`, restart docs, and README pointers.
- Non-goals: No frontend framework unless explicitly authorized, no real client data, no live Plaid, no production client portal, no autonomous investment advice.
- Acceptance criteria: Implemented baseline: UI defines shared context once, generates a compact ordered report view list, supports open/collapse, duplicate, change lens, change metric, client-facing/advisor-only status, reorder, and remove, switches between Builder Mode and Client Preview Mode, uses one existing `/api/runs` call plus safe report artifact fetches for concrete findings where available, saves a demo-local browser-state placeholder, hides technical/admin artifacts from the main path, and reduces headings/repeated explanatory text.
- Stop conditions: Implementation requires production auth, real client personalization, external APIs, or major backend schema decisions beyond the UI batch.

## Batch 16A-7a: Single Report Spec Composer

- Goal: Replace the too-dense local briefing-set UI with a sparse one-question-at-a-time composer for a single report spec.
- Mode: Superseded local UI baseline.
- Allowed scope: `src/arangur/app/static/index.html`, tests, restart docs, and README pointers.
- Non-goals: No report generation, no `/api/runs` call from the UI, no report links, no JSON links, no client preview, no technical/admin appendix, no multiple report view rows, no backend changes.
- Acceptance criteria: Implemented baseline: page shows `Arangur`, one current question on the left, completed report-spec lines on the right, empty state `No answers yet.`, Back and Start over behavior, six scripted questions, `Report spec complete`, and a placeholder `Add this report to briefing set` action.
- Stop conditions: Next behavior after adding the report spec requires product direction before implementation.

## Batch 16A-7b: Report Element Spec Composer v3.1

- Goal: Model one report element at a time across two separate branches: Client Briefing Set and Advisor Review Set.
- Mode: Implemented local UI baseline.
- Allowed scope: `src/arangur/app/static/index.html`, tests, restart docs, and README pointers.
- Non-goals: No report generation, no charts, no workflow API call from the UI, no report links, no client preview, no technical/admin artifact browser, no backend changes.
- Acceptance criteria: Implemented baseline: client/portfolio context appears first; branch is required; Client Briefing elements use client package placement; Advisor Review elements use advisor review placement plus internal purpose; intent is separate from element type; scope, lens, metric, scenario, and display are separate axes; plain `Manager` is not a lens option; scenario and lens completeness are acknowledged with demo/static badges; compact specs are added to the correct separate set list; Advisor Review rows include a promote placeholder.
- Stop conditions: Durable metadata, report generation, or persistence requires a follow-up contract batch.

## Batch 16A-7c: Report Element Template Catalog

- Goal: Add a static/mock report-element template catalog and backend catalog API so future UI discovery is template-driven rather than a fixed questionnaire.
- Mode: Implemented backend/catalog baseline.
- Allowed scope: `src/arangur/`, `src/arangur/app/`, tests, `docs/contracts/`, restart docs, and README pointers.
- Non-goals: No report generation, no charts, no UI rewrite, no saved report specs, no Docker/Postgres changes, no live Plaid, no external APIs, no real data.
- Acceptance criteria: Implemented baseline: `src/arangur/report_elements/templates.json` defines Portfolio Status, Concentration, Scenario Impact by Manager, Cash Generation Summary, Manager Comparison, and Data Confidence Note templates; `catalog.py` loads, validates, lists, looks up, and filters templates; `/api/report-elements` and `/api/report-elements/{element_id}` expose discovery/detail JSON; tests cover required fields, uniqueness, scenario requirements, scope/lens distinction, filters, and 404 behavior.
- Stop conditions: A future UI rewrite or durable spec persistence should be handled in separate batches.

## Batch 16A-7d: Catalog-Driven Report Element Composer UI

- Goal: Wire the browser composer to the report-element template catalog so discovery precedes element-specific configuration.
- Mode: Implemented local UI baseline.
- Allowed scope: `src/arangur/app/static/index.html`, tests, restart docs, contracts/docs clarifications, and README pointers.
- Non-goals: No report generation, no charts, no workflow API calls, no report links, no saved specs, no backend persistence, no Docker/Postgres changes, no live Plaid, no external APIs, no real data.
- Acceptance criteria: Implemented baseline: UI fetches `/api/report-elements`, provides branch/search/category/topic discovery, updates candidate templates locally, lets the advisor select a template immediately, renders only configuration fields derived from that template, skips scenario for `not_applicable` templates, keeps plain `Manager` out of lens options, and adds compact local specs to separate Client Briefing Set and Advisor Review Set lists with simple local row controls.
- Stop conditions: Durable serialization/export/import and backend spec persistence remain follow-up batches.

## Batch 16A-7e: Report Element Finder and Dynamic Configuration UI

- Goal: Refine the catalog-driven composer into a lighter finder-first UI that does not show the full catalog or a universal configuration form.
- Mode: Implemented local UI refinement.
- Allowed scope: `src/arangur/app/static/index.html`, tests, restart docs, and README pointers.
- Non-goals: No report generation, no charts, no workflow API calls, no report links, no backend persistence, no Docker/Postgres changes, no live Plaid, no external APIs, no real data.
- Acceptance criteria: Implemented baseline: context is a single compact line; target set is chosen before discovery; finder uses search, category browsing, and guided filters; initial state does not show all templates; candidate rows are compact; selected templates show preview before `Use this element`; right-side configuration omits Branch, hides fixed metric/display in details, asks only meaningful selected-template fields, and keeps placement under `Add to set as`; validation is quiet with `Ready to add`; two compact set lists remain.
- Stop conditions: Durable spec serialization/export/import and backend spec persistence remain follow-up batches.

## Batch 16A-7f: Compact Catalog Browse And Narrative Elements

- Goal: Add an experienced-user browse-all path and manual narrative/text elements to the local Report Element Finder.
- Mode: Implemented local UI refinement.
- Allowed scope: `src/arangur/app/static/index.html`, tests, restart docs, and README pointers.
- Non-goals: No report generation, no charts, no client preview, no workflow API calls, no AI narrative generation, no backend persistence, no Docker/Postgres changes, no live Plaid, no external APIs, no real data.
- Acceptance criteria: Implemented baseline: `Browse all templates` opens a compact category-grouped one-line-per-template catalog; selecting from that grouped list reuses the template preview/configuration flow; `Add narrative element` supports client briefing narrative types and advisor review narrative types; narrative rows appear in the same ordered set lists as analytic elements, are visually distinct, and support edit, duplicate, move up/down, and remove.
- Stop conditions: Durable spec serialization/export/import and backend spec persistence remain follow-up batches.

## Batch 16A-7g: Compact Grouped Template Picker Refinement

- Goal: Replace the inline browse-all catalog area with an attached compact grouped picker for fast template selection.
- Mode: Implemented local UI refinement.
- Allowed scope: `src/arangur/app/static/index.html`, tests, restart docs, and README pointers.
- Non-goals: No finder redesign, no modal, no report generation, no charts, no workflow API calls, no AI narrative generation, no backend persistence, no Docker/Postgres changes, no live Plaid, no external APIs, no real data.
- Acceptance criteria: Implemented baseline: `Browse all templates` toggles an attached dropdown-style picker near the button; categories are clear rows; templates are indented one-line rows without long descriptions, branch/topic chips, scenario badges, fixed metric/display, or coverage information; selecting a template closes the picker and reuses the existing selected-template preview and `Use this element` flow; the default empty state and search/category/filter candidate behavior remain unchanged.
- Stop conditions: Durable spec serialization/export/import and backend spec persistence remain follow-up batches.

## Batch 16A-7h: Report Element Finder / Composer Current Model Docs

- Goal: Stabilize documentation for the current Report Element Finder / Composer model before implementing serialization/export.
- Mode: Implemented documentation stabilization batch.
- Allowed scope: `docs/ui_reporting/`, `docs/contracts/`, `docs/restart/`, and README pointers.
- Non-goals: No UI behavior changes, no serialization/export implementation, no report generation, no charts, no client preview, no workflow API calls, no backend persistence, no Docker/Postgres changes, no live Plaid, no external APIs, no real data.
- Acceptance criteria: Implemented baseline: `docs/ui_reporting/report_element_finder_composer_current_model_v1.md` documents the current workflow, Client Briefing Set vs Advisor Review Set, discovery versus configuration, template-specific fields, scope/lens/scenario distinctions, metric/measure behavior, display/formatting boundaries, narrative elements, demo limitations, and next actions; contract, README, and restart docs point future batches toward spec-set serialization/export before report generation.
- Stop conditions: Product model contradictions, code changes, real data, credentials, legacy MATLAB inspection, report generation, or persistence implementation remain out of scope.

## Batch 16A-8: Report Element Spec Set Serialization / Export

- Goal: Serialize/export completed local Client Briefing Set and Advisor Review Set specs without generating reports.
- Mode: Recommended implementation batch after the current model documentation is stable.
- Allowed scope: likely `src/arangur/app/static/index.html`, tests, `docs/contracts/`, `docs/ui_reporting/`, restart docs, and README pointers.
- Non-goals: No report generation, no chart generation, no client preview rendering, no workflow API calls from the composer, no backend persistence, no Docker/Postgres changes, no live Plaid, no external APIs, no real data.
- Acceptance criteria: The local browser composer can produce a deterministic JSON-friendly representation of the ordered Client Briefing Set and Advisor Review Set, including analytic elements, narrative elements, target set, placement, element order, selected template IDs, configured parameters, narrative fields, and catalog/version metadata where available; export/copy behavior is local-only and does not call report generation APIs.
- Stop conditions: Export shape requires unresolved product decisions, durable backend persistence is needed, report generation is requested, or client-facing preview/rendering becomes necessary.

## Batch 16A-8b: Briefing Set Metadata

- Goal: Add selected report element specs and briefing set metadata to backend/report packages after the local spec-set shape is stable.
- Mode: Recommended implementation/design batch after the UI model is stable.
- Allowed scope: `src/`, `tests/`, `docs/contracts/`, `docs/ui_reporting/`, and generated synthetic report artifacts if intentionally refreshed.
- Non-goals: No production persistence model for real clients, no full portfolio database redesign, no live data.
- Acceptance criteria: Report packages can represent shared briefing context, selected report element specs, report view sequence, visibility status, audience depth, and client preview metadata while preserving existing workflow-run compatibility.
- Stop conditions: Schema changes threaten current API compatibility or require unresolved product decisions.

## Batch 16A-9: Client Preview Sequence Rendering

- Goal: Render client preview from the selected ordered report views instead of from a static generic briefing page.
- Mode: Recommended implementation batch.
- Allowed scope: `src/arangur/app/`, `src/arangur/` for small metadata helpers if needed, tests, docs, and synthetic generated artifacts if intentionally refreshed.
- Non-goals: No PDF/export workflow, no production client portal, no recommendation engine.
- Acceptance criteria: Client preview shows selected client-facing report views in order, uses concrete portfolio-derived findings where available, hides advisor-only views and technical/admin artifacts, and updates when the builder list is reordered or edited.
- Stop conditions: Client-facing language requires product/legal review beyond existing demo caveats.

## Batch 16A-10: Save/Load Briefing Set Skeleton

- Goal: Add a first skeleton for saving and reopening synthetic/demo briefing sets.
- Mode: Future implementation batch after report view and preview behavior are stable.
- Allowed scope: To be defined later, likely `src/arangur/app/`, tests, docs, and optional file-backed/demo persistence.
- Non-goals: No production client data, no multi-tenant entitlement model, no real document export.
- Acceptance criteria: A demo briefing set can be saved with shared context and ordered report views, reopened, and previewed without exposing technical/admin artifacts in the main path.
- Stop conditions: Persistence choices require production account modeling or real client data.

## Batch 16B: Briefing Story Mapping Layer

- Goal: Add a small mapping layer from canonical client questions to internal workflow types and briefing metadata.
- Mode: Recommended implementation/design batch after sparse guided builder baseline, unless backend metadata is needed first.
- Allowed scope: `src/`, `tests/`, `docs/ui_reporting/`, `docs/contracts/`, and generated synthetic demo artifacts if intentionally refreshed.
- Non-goals: No LLM integration, no production personalization, no real client history.
- Acceptance criteria: Supported client questions map to internal workflows, audience modes, report section defaults, and evidence requirements; tests verify mappings.
- Stop conditions: Mapping requires real client conversation data or unresolved product decisions.

## Batch 16C: Audience-Depth Report Handling

- Goal: Add audience depth metadata and rendering behavior to report packages and generated reports.
- Mode: Recommended implementation batch.
- Allowed scope: `src/`, `tests/`, `docs/contracts/`, `docs/ui_reporting/`, and `reports/demo/` generated outputs.
- Non-goals: No full client portal, no real data, no production compliance workflow.
- Acceptance criteria: Report packages record audience depth; generated reports can distinguish Standard Family Office Meeting, Executive, Analytical Stakeholder, and Advisor/Internal levels at least in section detail and caveat depth.
- Stop conditions: Client-facing language requires product/legal review beyond demo caveats.

## Batch 16D: Manager-Role Review Prototype

- Goal: Prototype the first `Why do we own Manager 5?` briefing path using current manager allocation, exposure, overlap, scenario, and data confidence outputs.
- Mode: Recommended implementation batch.
- Allowed scope: `src/`, `tests/`, `docs/ui_reporting/`, `docs/demo/`, and generated synthetic reports.
- Non-goals: No manager recommendations, no real manager due diligence, no fund look-through unless synthetic only.
- Acceptance criteria: The path compares Manager 5 against other managers across available categories/themes/scenario behavior, flags possible shadowing as a mandate question, and avoids automatic action recommendations.
- Stop conditions: Real manager data, real mandates, or investment recommendation language appears necessary.

## Batch 17: Docker Compose Local Private Demo

- Goal: Add the local Docker private-demo stack using the Education pattern.
- Mode: Implemented local/private-demo packaging baseline.
- Allowed scope: `Dockerfile`, Docker Compose files, `.env.private-demo.example`, `docs/deployment/`, app settings/tests, and README.
- Non-goals: No real `.env.private-demo`, no committed secrets, no AWS managed services, no production hardening claims.
- Acceptance criteria: Implemented baseline and Frank runtime-smoked locally: Compose config defines app and internal Postgres services, app uses `DATABASE_URL` to reach `postgres`, `/api/health` returns `status: ok` with private-demo/Postgres settings, `/app/` loads, Postgres-backed briefing spec-set POST/list works, and docs explain local smoke checks.
- Stop conditions: Secrets, actual hostnames, or infrastructure choices beyond Lightsail/Caddy/Cloudflare become required.

## Batch 18: Demo Seed And Preflight Scripts

- Goal: Add seed/preflight commands that exercise real app/service paths and create deterministic private-demo workflow runs.
- Mode: Partially implemented local preflight baseline; workflow-run seed remains future.
- Allowed scope: `src/`, `tests/`, `docs/deployment/`, README, and scripts if the repo adopts a scripts folder.
- Non-goals: No fake DB-only seed rows, no external APIs, no live Plaid, no real data.
- Acceptance criteria: Implemented preflight baseline: smoke script verifies health, static app, report-element catalog, and Postgres-backed briefing spec-set save/list through real HTTP paths using synthetic/demo data only and without requiring Docker in tests. Remaining future seed: create native quarterly, native data coverage, and Plaid-shaped intake runs through existing app paths if explicitly authorized.
- Stop conditions: Seed data needs real credentials, real source data, or deployment-specific hostnames.

## Batch 19: Lightsail Deployment Docs

- Goal: Document the first Lightsail Ubuntu, Caddy, Cloudflare, and Docker Compose deployment process for the private demo.
- Mode: Documentation batch.
- Allowed scope: `docs/deployment/`, `docs/decisions/`, `docs/restart/`, and README pointers.
- Non-goals: No actual server provisioning from Codex, no secrets, no live DNS mutation, no AWS managed RDS/ECS.
- Acceptance criteria: Docs cover host prep, env file creation, Compose startup, Caddy reverse proxy, Cloudflare DNS, health/smoke checks, rollback/restart basics, and production-security non-claims.
- Stop conditions: Actual public subdomain choice, credentials, or cloud account actions are required.

## Batch 20: Generated Report Artifact Model

- Goal: Define the first generated report artifact product object between saved workflows and Presentation.
- Mode: Implemented model/contract baseline.
- Allowed scope: `src/arangur/report_elements/`, tests, `docs/contracts/`, and restart docs.
- Non-goals: No Populate workflow UI, no Present/report library UI, no generated report history, no backend schema, no Docker/deployment changes, no new analytics, no live data, and no real client data.
- Acceptance criteria: Implemented baseline: deterministic client briefing and advisor review artifacts can be built from existing preview fixtures with report metadata, source workflow fields, dated data snapshot fields, ordered sections, caveats, text/HTML content, validation, and `demo_partial` status.
- Stop conditions: Artifact creation requires new analytics, simulation changes, database schema changes, UI redesign, generated report history, real data, external APIs, or new dependencies.

## Batch 21: Demo Workflow Population To Report Artifacts

- Goal: Wire a browser-local saved workflow and current synthetic demo data snapshot into the generated report artifact model.
- Mode: Implemented product-path/API/UI batch.
- Allowed scope: `src/arangur/app/`, the generated artifact model if needed, tests, generated artifact contract docs, restart docs, and README copy.
- Non-goals: No generated report library UI, no generated report history, no Present/report library implementation, no backend database schema, no Docker/deployment changes, no new analytics, no simulation changes, no live data, no real client data, no external APIs, and no dependencies.
- Acceptance criteria: Implemented baseline: `POST /api/generated-reports/demo-populate` accepts representative Client Briefing and Advisor Review browser workflow payloads, returns `generated_report_artifact.v1`, uses `Current synthetic demo snapshot` / `2026-06-30`, stays deterministic and Postgres-free, rejects invalid report types and missing sets, and the Populate UI can create/open a clean demo populated report artifact view without exposing raw artifact JSON.
- Stop conditions: Further work should stop if it requires durable report history, production report library decisions, database schema changes, new analytics, simulation changes, real data, external API calls, production auth, or deployment changes.

## Batch 22: Local Generated Report Presentation Shelf

- Goal: Store Populate-created generated report artifacts in the browser and make Present / view reports minimally real.
- Mode: Implemented product-path/UI batch.
- Allowed scope: `src/arangur/app/static/index.html`, tests, generated artifact contract docs, restart docs, and README copy.
- Non-goals: No backend generated report persistence, no database tables, no backend list endpoints, no full report library/history, no search/filter/version UI, no Docker/deployment changes, no live data, no real client data, no external APIs, and no dependencies.
- Acceptance criteria: Implemented baseline: Populate saves successful `generated_report_artifact.v1` responses to browser `localStorage` under `arangur.local_generated_reports.v1`, keyed by artifact `report_id`; Present / view reports lists the local generated report shelf, opens a clean Generated report presentation view with source workflow, report type, generated/data-as-of metadata, Back to Home, Back to Reports, Print, Export HTML, and Copy text; deleting a shelf record does not delete the source saved workflow; the advisor path still avoids raw artifact JSON and does not call `/api/runs`.
- Stop conditions: Further work should stop if it requires backend report history, production report library decisions, database schema changes, generated report versioning, real data, external API calls, production auth, or deployment changes.

## Batch 23: Generated Report Demo Content

- Goal: Make the first generated Client Briefing and Advisor Review read like coherent advisor product content.
- Mode: Implemented content/product-path batch.
- Allowed scope: `src/arangur/report_elements/`, small generated-report assembly copy, deterministic briefing preview fixtures, tests, restart docs, and brief contract/README notes.
- Non-goals: No new analytics, simulation kernel changes, UI redesign, backend generated report persistence, report library/history, Docker/deployment changes, live data, real client data, external APIs, or dependencies.
- Acceptance criteria: Implemented baseline at the time: default generated artifacts were made more product-readable using existing rendered fragments and synthetic data. Superseded for saved-workflow Populate artifacts by Batch 26: generated report body sections now preserve the advisor-authored workflow instead of adding automatic narrative framing or alternate section titles. Narrative sections still render as natural headings/body text without visible metadata wrappers; unsupported sections keep calm nontechnical placeholders.
- Stop conditions: Further work should stop if it requires new analytics, simulation changes, product/legal language review beyond demo caveats, backend report history, database schema changes, real data, external API calls, production auth, or deployment changes.

## Batch 24: Private Demo Walkthrough Checklist

- Goal: Add a concise end-to-end private-demo walkthrough and QA checklist for the current saved workflow -> populated report -> presentation path.
- Mode: Implemented QA/readiness/documentation batch.
- Allowed scope: `docs/demo/`, README/private-demo runbook links, restart docs, and static tests.
- Non-goals: No new product features, UI redesign, new top-level Advisor Home choices, report library/history, backend generated report persistence, Docker services, deployment configuration, production auth, real data, external APIs, or dependencies.
- Acceptance criteria: Implemented baseline: `docs/demo/private_demo_walkthrough.md` covers Windows cmd stack startup, smoke script, app URL, Advisor Home click-through, Client Briefing Workflow creation, save/populate/open generated report, Present / view reports shelf open, Print / Export HTML / Copy text confirmation, optional Advisor Review repeat, stack shutdown, pass/fail QA checks, and current synthetic/browser-local limitations; README and the private-demo Docker doc link to it; static tests assert the walkthrough references without requiring Docker runtime.
- Stop conditions: Further walkthrough/checklist work should stop if it requires UI redesign, product behavior changes, Docker runtime in unit tests, real data, secrets, external APIs, backend persistence, generated report history, or deployment decisions.

## Batch 25: Generated Report Workflow Identity Fix

- Goal: Fix stale-state mixing during Populate workflow with data and generated report creation/opening.
- Mode: Implemented bug-fix batch.
- Allowed scope: `src/arangur/app/static/index.html`, generated-report assembly, artifact title metadata, focused tests, restart docs, and a tiny walkthrough clarification.
- Non-goals: No new product features, UI redesign, top-level Advisor Home choices, report library/history, backend generated report persistence, database tables/endpoints, Docker/deployment changes, production auth, real data, external APIs, simulation changes, analytics changes, or dependencies.
- Acceptance criteria: Implemented baseline: Populate resolves the selected saved workflow by `workflow_id` at the moment `Create demo populated report` is clicked, uses that saved workflow's payload and display name for source workflow id/name/title/sections, blocks calmly if the saved workflow cannot be found, shows a small source workflow confirmation, skips malformed old generated report shelf records, and uses a per-population request id in `report_id` so repeated Populate actions create distinct browser-local shelf records.
- Stop conditions: Further work should stop if it requires backend persistence/schema changes, generated report history, report library UI, UI redesign, Docker changes, new dependencies, real data, secrets, external APIs, or deployment decisions.

## Batch 26: Generated Report Preview Alignment

- Goal: Align Preview, Populate, and Present so generated reports faithfully render the selected advisor-authored workflow sequence.
- Mode: Implemented correctness/alignment batch.
- Allowed scope: `src/arangur/app/static/index.html`, `src/arangur/app/generated_reports.py`, `src/arangur/report_elements/generated_report_artifact.py`, focused tests, generated artifact contract docs, restart docs, and README copy.
- Non-goals: No new product features, UI redesign, top-level Advisor Home choices, report history/library, backend generated report persistence, database tables/endpoints, Docker/deployment changes, production auth, real data, external APIs, simulation changes, analytics changes, or dependencies.
- Acceptance criteria: Implemented baseline: generated report `ordered_sections` now contain only the advisor-authored workflow body; automatic framing, closing prompts, follow-up sections, and caveat body sections are not inserted; narrative section titles/text and selected template titles are preserved in order; matched analytic sections reuse rendered fragment detail comparable to Preview; report metadata/caveats remain header/footer/top-level metadata; Present shelf rows show source workflow, local generated timestamp, and data snapshot label; deleting or clearing generated report shelf records does not delete saved workflows.
- Stop conditions: Further work should stop if alignment requires new analytics, simulation changes, backend schema/persistence, a full report library/history feature, UI redesign, Docker changes, new dependencies, real data, secrets, external APIs, or deployment decisions.

## Batch 27: Post-Fix Private Demo Rehearsal Checkpoint

- Goal: Record the successful local private-demo browser rehearsal after the generated-report preview alignment fix.
- Mode: Implemented documentation-only checkpoint.
- Allowed scope: restart docs and private-demo walkthrough notes.
- Non-goals: No app behavior changes, UI changes, tests, backend endpoints, Docker changes, deployment, dependencies, secrets, env inspection, or pushes.
- Acceptance criteria: Implemented baseline: docs record that Frank manually verified Docker stack startup, smoke script, authored workflow preview, copied-workflow Populate, generated report sequence, removal of automatic framing/closing sections, and Present / view reports opening after commit `524a99b`.
- Next decision options: one clean-state private-demo walkthrough, product-polish fixes for remaining local rehearsal issues, workflow/generated-report naming or local reset cleanup, or report-content improvements for specific report elements. Private-server deployment planning is not the immediate next action.

## Batch 28: Local Product Readiness Checkpoint

- Goal: Keep the project on the pre-deployment local product/readiness path after the successful post-fix browser rehearsal.
- Mode: Implemented documentation-only checkpoint.
- Allowed scope: restart docs and private-demo walkthrough notes.
- Non-goals: No AWS, Lightsail, Caddy, Cloudflare, Docker, app behavior, UI, backend endpoint, dependency, real-data, secret, or deployment changes.
- Acceptance criteria: Implemented baseline: docs record that the generated-report alignment fix passed manual browser rehearsal, the prior Populate/generated-report mismatch is fixed, generated reports preserve the advisor-authored workflow body, automatic framing/closing sections are no longer inserted, Present / view reports opens generated reports correctly, and the Docker/private-demo stack remains local only.
- Next recommended path: run one clean-state private-demo walkthrough, fix remaining local product issues, optionally tighten workflow/generated-report naming and local reset behavior, and optionally improve specific report-element content. Return to private-server deployment planning only after an explicit later decision.

## Batch 29: Arranger Analytic Control Plane Contracts

- Goal: Define the Arranger internal analytic control-plane boundary and first analytic pack contract.
- Mode: Implemented architecture/contracts/fixtures/tests batch.
- Allowed scope: architecture docs, contract docs, restart docs, a tiny README pointer, minimal synthetic analytic-pack fixtures, and static/contract tests.
- Non-goals: No advisor-facing UI, Arranger Studio UI, backend endpoints, Docker/deployment changes, scenario math, covariance/PCA/key-rate engines, simulation-kernel changes, live data, external APIs, real client data, secrets, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: docs define the Arranger publish / Arangur consume boundary; the analytic pack contract names manifest, theme catalog, lens catalog, scenario catalog, scenario shock pack, data confidence rule catalog, and report analytic capability map components; the fixture pack marks itself synthetic/demo and references current report element ids; and standard-library tests validate the fixture shape and boundary language.
- Next recommended path: build Arranger Demo Analytic Pack v1 content. Fill in richer approved themes, scenario stories, demo shock assumptions, confidence rules, and report-element compatibility details without exposing control-plane machinery in the advisor app.

## Batch 30: First Analytic Pack Proof Outputs

- Goal: Expand the Arranger Demo Analytic Pack v1, add a lightweight loader/validator, and apply the pack to existing synthetic portfolio/scenario/valuation fixtures.
- Mode: Implemented data/contracts/source/tests/docs batch.
- Allowed scope: analytic pack fixture, `src/arangur/analytics/`, deterministic analytics outputs under `data/simulation/analytics/`, tests, contract/architecture/restart docs, and a small README pointer.
- Non-goals: No advisor UI, Arranger Studio UI, report builder changes, new report elements, report-element input mapping, generated-report wiring, backend endpoints, Docker/deployment changes, production auth, live data, Plaid, external APIs, real data, simulation-kernel changes, covariance/PCA/key-rate engines, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: pack content is curated but meaningful; loader/validator catches shape and reference issues; proof generator writes theme exposure, manager/theme overlap, scenario impact by theme/manager, data confidence map, cross-scenario resilience summary, and output index; tests validate deterministic generation, required output fields, scenario ids, plausible percentages, no external API dependency, and no control-plane UI.
- Next recommended path: implemented by Batch 31 below.

## Batch 31: Analytic Proof Outputs To Report Views

- Goal: Map the synthetic analytics proof outputs into current report-element input payloads and rendered report-element views where the existing catalog supports it.
- Mode: Implemented source/data/tests/docs batch.
- Allowed scope: `src/arangur/report_elements/`, deterministic report-element input/view fixtures under `data/simulation/`, focused tests, contract/architecture/restart docs, and a small README pointer.
- Non-goals: No advisor UI, Arranger Studio UI, new report elements, generated-report wiring, backend endpoints, Docker/deployment changes, charts, live data, external APIs, real data, simulation-kernel changes, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: analytic proof outputs now map into separate report-element input payloads for Concentration, Manager Comparison, Scenario Impact by Manager, Data Confidence Note, and Portfolio Status; renderer output writes view JSON plus Markdown/HTML fragments with a separate analytic summary; tests validate input mapping, rendering, legacy summary isolation, no path leakage in fragments, and no UI/generated-report surfaces. Cash Generation Summary remains on the existing simulation-derived path because no simple cash-specific analytic proof source was added.
- Next recommended path: implemented by Batch 32 below.

## Batch 32: Arangur Analytics Consumption v1

- Goal: Wire approved analytic pack choices and analytic-derived report views into the existing Advisor workflow Preview, Populate, and Present paths.
- Mode: Implemented product-path/source/tests/docs batch.
- Allowed scope: static Advisor app, report-element matching/loading, template metadata, focused tests, contracts/architecture/restart docs, and small README guidance.
- Non-goals: No Arranger Studio UI, control-plane UI, new top-level Advisor Home choices, backend endpoints, Docker/deployment changes, production auth, live data, Plaid, external APIs, real data, simulation-kernel changes, covariance/PCA/key-rate engines, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: relevant templates expose approved pack-driven theme, lens, scenario, and confidence-focus labels; the static app reads both legacy and analytic rendered-view summaries; supported configured specs resolve to analytic-derived fragments for Portfolio Status, Concentration, Manager Comparison, Scenario Impact by Manager for AI / Chip Selloff, and Data Confidence Note; Populate recomputes view matches from saved configured parameters; Present opens the same generated report sections; generated reports preserve advisor-authored order and narrative sections; unsupported selections such as Rate Shock scenario impact remain advisor-safe placeholders.
- Next recommended path: run one clean local demo walkthrough using analytic-aware workflow elements, then either polish the analytic report content or tighten naming/local reset behavior based on rehearsal notes. Deployment remains parked until a later explicit decision.

## Batch 33: Arranger Internal Analytics Algorithm Design v1

- Goal: Define the internal algorithm architecture behind the analytic control plane before adding more implementation.
- Mode: Implemented architecture/design-only checkpoint.
- Allowed scope: architecture docs, restart docs, and tiny README pointers.
- Non-goals: No production code, app behavior changes, advisor UI, Arranger Studio UI, backend endpoints, Docker/deployment changes, scenario-engine runtime, covariance/PCA runtime, live data, external APIs, real data, secrets, dependencies, or pushes.
- Acceptance criteria: Implemented baseline, then revised in the follow-up design-alignment checkpoint: `docs/architecture/arranger_internal_analytics_algorithm_design_v1.md` defines the internal publish-consume boundary and now centers full portfolio revaluation as the scenario methodology. It defines full market state, scenario market state, key-rate expansion, full position valuation, portfolio revaluation, post-valuation attribution, theme/classification rules, coverage/confidence handling, advisor consumption rules, implementation sequence, and open questions for Frank.
- Next recommended path: design and implement a full revaluation scenario-engine skeleton. The first implementation should produce base/scenario position revaluation results and a revaluation bundle manifest before further advisor UI/report consumption work expands.

## Batch 34: Full Revaluation Analytics Design Alignment

- Goal: Correct the internal analytics methodology around full portfolio revaluation before implementation continues.
- Mode: Implemented architecture/contracts/restart documentation checkpoint.
- Allowed scope: architecture docs, contract docs, restart docs, and tiny README pointers.
- Non-goals: No production code, app behavior changes, advisor UI, report views, generated analytics outputs, backend endpoints, Docker/deployment docs, live data, external APIs, real data, secrets, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: docs state that scenario impact is calculated only by valuing every position under a base market state and under a complete scenario market state, then aggregating scenario value minus base value. Scenario construction now expands approved key-rate/driver perturbations into complete market input surfaces; themes are attribution/reporting layers after valuation; coverage/confidence language describes revaluation limitations; advisor-facing Arangur consumes approved outputs and does not expose construction machinery.
- Next recommended path: full revaluation scenario-engine skeleton using existing synthetic fixtures, with `value_position(position, market_state, valuation_context)`, base/scenario position valuation records, post-valuation attribution, confidence/coverage summaries, and a revaluation bundle manifest.

## Batch 35: Key Market-State Scenario Basis Design v1

- Goal: Define how Arranger constructs complete scenario market states from a compact, curated set of key market-state coordinates.
- Mode: Implemented architecture/design-only checkpoint.
- Allowed scope: architecture docs, restart docs, contract docs if needed, and tiny README pointers.
- Non-goals: No production code, app behavior changes, advisor UI, report views, generated analytics outputs, backend endpoints, Docker/deployment docs, live data, external APIs, real data, secrets, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: `docs/architecture/key_market_state_scenario_basis_design_v1.md` defines Scenario Basis Models, price-coordinate representation, multiple possible basis models, extraction/anchor/completion/validation/expansion algorithms, deterministic and reduced covariance/PCA completion methods, expansion dispatch to full market-state inputs, validation layers, interaction with full revaluation, and the boundary with themes/position mapping.
- Next recommended path: completed by Batch 36 for thesis-specific classification lenses. Remaining design gap is position-to-market-input / valuation coverage mapping. After that, implement scenario basis contract files, one Broad Multi-Asset Basis fixture, deterministic completion, simple market-state expansion, and then the full revaluation skeleton.

## Batch 36: Thesis Lens Position Mapping Design v1

- Goal: Define how Arranger maps positions into complete thesis-specific classification lenses.
- Mode: Implemented architecture/design-only checkpoint.
- Allowed scope: architecture docs, restart docs, contract docs if needed, and tiny README pointers.
- Non-goals: No production code, app behavior changes, advisor UI, report views, generated analytics outputs, backend endpoints, Docker/deployment docs, live data, external APIs, real data, secrets, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: `docs/architecture/thesis_lens_position_mapping_design_v1.md` defines thesis lenses, thesis buckets, secondary flags, evidence packets, completeness/orthogonality rules, example AI Adoption / Deglobalization / Geopolitical Bloc / Energy Security / Credit Stress / Private Liquidity schemas, deterministic classification precedence, internal LLM-assisted classification policy, published mapping artifacts, full-revaluation aggregation, advisor consumption rules, sequencing, and open questions.
- Next recommended path: completed by Batch 37 for position valuation coverage mapping. Implementation can begin with a full revaluation engine skeleton if Frank approves.

## Batch 37: Position Valuation Coverage Mapping Design v1

- Goal: Define how Arranger maps positions to instruments, pricing functions, required market inputs, valuation results, and explicit coverage statuses.
- Mode: Implemented architecture/design-only checkpoint.
- Allowed scope: architecture docs, restart docs, contract docs if needed, and tiny README pointers.
- Non-goals: No production code, app behavior changes, advisor UI, report views, generated analytics outputs, backend endpoints, Docker/deployment docs, live data, external APIs, real data, secrets, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: `docs/architecture/position_valuation_coverage_mapping_design_v1.md` defines the universal pricing-function interface, instrument and position schemas, pricing-function registry, required market input mapping, coverage status policies, asset-class treatment examples, valuation result/cash-flow shape, base/scenario comparison, scenario-basis and thesis-lens boundaries, internal review/governance, published valuation coverage artifacts, advisor-facing consumption rules, sequencing, and open questions.
- Next recommended path: if Frank approves implementation, build the first synthetic full revaluation engine skeleton with scenario basis fixtures, instrument/position/pricing-function coverage fixtures, base/scenario valuation results, position comparisons, and a revaluation bundle manifest before returning to thesis-bucket/report aggregation.

## Batch 38: Synthetic Full Revaluation Engine Skeleton v1

- Goal: Implement the first internal full revaluation skeleton from synthetic fixtures.
- Mode: Implemented source/data/tests/docs checkpoint.
- Allowed scope: `src/arangur/analytics/`, `data/simulation/revaluation/`, tests, restart docs, and README pointers.
- Non-goals: No advisor UI, report views, backend endpoints, Docker/deployment changes, auth, secrets, Plaid, live market data, external APIs, real data, production pricing, covariance/PCA runtime, dependencies, or pushes.
- Acceptance criteria: Implemented baseline: `src/arangur/analytics/pricing_functions.py` defines the approved synthetic pricing function registry implementations; `src/arangur/analytics/revaluation.py` builds instrument/position catalogs, market states, coverage maps, valuation results, position comparisons, portfolio summary, coverage manifest, and bundle manifest; `src/arangur/analytics/revaluation_runner.py` regenerates the bundle with `python -m arangur.analytics.revaluation_runner`; and `data/simulation/revaluation/` contains deterministic committed artifacts for the `ai_chip_selloff` scenario. Tests cover fixture references, pricing assignment, base/scenario valuation rows, scenario market-state source use, reconciliation, determinism, and no external API/shortcut markers.
- Next recommended path: decide whether to broaden internal valuation coverage/scenario breadth, map the revaluation bundle into analytic/report-element input fixtures, improve specific report content, or begin thesis-lens aggregation on top of the revalued position impacts. Deployment planning remains parked until explicitly authorized.
