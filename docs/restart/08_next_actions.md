# Next Actions

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
