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
- Acceptance criteria: Report sections are clearer, tables are consistently formatted, generated outputs remain deterministic, caveats remain prominent, and focused tests cover report generation.
- Stop conditions: Report claims could be confused with real advice, generated outputs require client data, or layout tooling becomes a dependency decision.

## Batch 5: Harden Analytics And Validation

- Goal: Harden deterministic valuation, exposure/overlap summaries, scenario shocks, validations, and edge-case handling after the first vertical slice exists.
- Mode: Implementation batch.
- Allowed scope: `src/`, `tests/`, `data/demo/`, `docs/contracts/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No vendor data, no full accounting, no advanced risk model, no Plaid.
- Acceptance criteria: Calculations have stronger validation, clearer errors, and tests for missing prices, duplicated IDs, cash, and scenario rule precedence.
- Stop conditions: Missing vertical slice, unresolved scenario methodology decision, or unsafe source data.

## Batch 6: Plaid-Shaped Mock Ingestion Adapter

- Goal: Add a mock adapter that looks like Plaid ingestion but uses local synthetic Plaid-shaped fixtures.
- Mode: Implementation batch.
- Allowed scope: `data/demo/`, `src/`, `tests/`, `docs/contracts/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No Plaid Sandbox, no live Plaid credentials, no external API calls.
- Acceptance criteria: Mock Plaid-shaped input produces the same canonical snapshot type as the demo data loader.
- Stop conditions: Live credentials appear necessary, external API access is required, or canonical snapshot gaps need product-owner decisions.

## Batch 7: Local Portfolio Viewer Spike

- Goal: Explore a simple local viewer for the generated demo outputs if Frank wants a visible product surface before Plaid-shaped ingestion.
- Mode: Design or implementation spike, depending on authorization.
- Allowed scope: `src/`, `reports/demo/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No production dashboard, no live APIs, no credentials, no real client data.
- Acceptance criteria: A simple local-only viewing path exists or a clear viewer design is documented.
- Stop conditions: UI scope becomes broad, dependencies become necessary, or product direction is unclear.

## Batch 8: Plaid Sandbox Integration Design

- Goal: Design the future Plaid Sandbox integration and operational boundaries.
- Mode: Design batch, possibly followed by implementation only if authorized.
- Allowed scope: `docs/architecture/`, `docs/contracts/`, `docs/decisions/`, `docs/restart/`, and possibly `src/` stubs if explicitly authorized.
- Non-goals: No live Plaid production access, no private credentials committed, no real client ingestion.
- Acceptance criteria: Sandbox flow, secrets policy, adapter contract, and test strategy are documented.
- Stop conditions: Credentials or account setup are required, strategy needs Frank, or implementation scope exceeds the design batch.
