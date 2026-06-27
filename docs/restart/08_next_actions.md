# Next Actions

## Batch 2: Architecture And Contracts For Thin Demo

- Goal: Expand architecture and contract docs enough to guide implementation.
- Mode: Documentation and schema-design batch.
- Allowed scope: `docs/architecture/`, `docs/contracts/`, `docs/demo/`, `docs/restart/`, and lightweight README pointers.
- Non-goals: No Plaid, no MATLAB audit, no real client data, no production UI.
- Acceptance criteria: Thin-demo components have clear inputs, outputs, invariants, and fixture expectations.
- Stop conditions: Existing substantial docs would be overwritten, secrets/client data appear necessary, or MATLAB inspection appears required.

## Batch 3: Demo Data Loader And Canonical Snapshot

- Goal: Implement simple local demo data loading and the first canonical portfolio snapshot.
- Mode: Implementation batch.
- Allowed scope: `data/demo/`, `src/`, `tests/`, `docs/contracts/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No Plaid, no live APIs, no deep valuation, no generated advisor report yet.
- Acceptance criteria: Synthetic fixtures load deterministically, canonical snapshot is produced, and focused tests pass.
- Stop conditions: Real data is encountered, schemas require unresolved product judgment, or implementation needs new dependencies without clear justification.

## Batch 4: Simple Valuation, Exposure, And Scenario Outputs

- Goal: Implement deterministic valuation, exposure/overlap summaries, and simple scenario shocks.
- Mode: Implementation batch.
- Allowed scope: `src/`, `tests/`, `data/demo/`, `docs/contracts/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No vendor data, no full accounting, no advanced risk model.
- Acceptance criteria: Demo snapshot produces valuation, exposure, overlap, and scenario result artifacts with tests.
- Stop conditions: Missing canonical contract, unresolved scenario methodology decision, or unsafe source data.

## Batch 5: First Advisor-Readable Demo Report

- Goal: Generate the first static advisor-readable report or viewer package from demo outputs.
- Mode: Implementation and documentation batch.
- Allowed scope: `src/`, `tests/`, `reports/demo/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No production report engine, no advisor assistant, no live client output.
- Acceptance criteria: A synthetic report is generated under `reports/demo/` and can be regenerated from local demo data.
- Stop conditions: Report claims could be confused with real advice, generated outputs require client data, or layout tooling becomes a dependency decision.

## Batch 6: Plaid-Shaped Mock Ingestion Adapter

- Goal: Add a mock adapter that looks like Plaid ingestion but uses local synthetic Plaid-shaped fixtures.
- Mode: Implementation batch.
- Allowed scope: `data/demo/`, `src/`, `tests/`, `docs/contracts/`, `docs/demo/`, and `docs/restart/`.
- Non-goals: No Plaid Sandbox, no live Plaid credentials, no external API calls.
- Acceptance criteria: Mock Plaid-shaped input produces the same canonical snapshot type as the demo data loader.
- Stop conditions: Live credentials appear necessary, external API access is required, or canonical snapshot gaps need product-owner decisions.

## Batch 7: Plaid Sandbox Integration Design

- Goal: Design the future Plaid Sandbox integration and operational boundaries.
- Mode: Design batch, possibly followed by implementation only if authorized.
- Allowed scope: `docs/architecture/`, `docs/contracts/`, `docs/decisions/`, `docs/restart/`, and possibly `src/` stubs if explicitly authorized.
- Non-goals: No live Plaid production access, no private credentials committed, no real client ingestion.
- Acceptance criteria: Sandbox flow, secrets policy, adapter contract, and test strategy are documented.
- Stop conditions: Credentials or account setup are required, strategy needs Frank, or implementation scope exceeds the design batch.
