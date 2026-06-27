# Decision Log

## Decision 0001: Build A Thin End-To-End Demo First

- Date: 2026-06-27.
- Decision: Build a thin end-to-end demo system before deep component rebuilds.
- Reason: A working pipeline will clarify product value, data contracts, and advisor-facing outputs faster than isolated engine work.
- Consequences: Initial components should be simple, deterministic, and replaceable. Deep valuation, full accounting, and production integrations wait until the demo path exists.

## Decision 0002: Plaid Is Early But Not First

- Date: 2026-06-27.
- Decision: Plaid ingestion should come early, but it is not the first organizing step.
- Reason: The system needs a canonical portfolio boundary before adding live or sandbox ingestion complexity.
- Consequences: Plaid should become one adapter that emits the canonical snapshot. The first demo uses local synthetic data.

## Decision 0003: Legacy MATLAB Is Read-Only Reference

- Date: 2026-06-27.
- Decision: Legacy MATLAB is read-only reference material until a specific audit batch is authorized.
- Reason: Treating MATLAB as the organizing center would slow the v2 demo and risk porting before product boundaries are clear.
- Consequences: Do not port, modify, or deeply inspect legacy MATLAB in ordinary v2 batches. Use it only when a targeted audit is authorized.

## Decision 0004: Documentation Is Restart-Oriented

- Date: 2026-06-27.
- Decision: Restart-oriented documentation should be maintained as a first-class project artifact.
- Reason: The project is being coordinated across Frank, ChatGPT, and Codex, so restarts need ordered context and current state.
- Consequences: Keep restart docs current after each meaningful batch. Future sessions should read the restart files in numeric order.

## Decision 0005: Stochastic Scenarios Are Future Roadmap, Not Current Implementation

- Date: 2026-06-27.
- Decision: Covariance-driven and random-number-driven scenario simulation should remain a future roadmap item, while the current demo uses deterministic scenario shocks.
- Reason: Deterministic shocks are explainable, testable, and sufficient for the thin demo. Stochastic simulation requires additional assumptions, data provenance, reproducibility controls, and caveats.
- Consequences: Current reports may show deterministic portfolio impact under stated assumptions. Future simulation work should include driver assumptions, seed values, covariance provenance, and reportable impact ranges before implementation.

## Decision 0006: Data Availability And Valuation Confidence Are A Formal Workstream

- Date: 2026-06-27.
- Decision: Arangur should maintain a formal data availability and valuation-confidence workstream before expanding into harder asset classes or production reporting.
- Reason: Real portfolios depend on uneven data quality, stale statements, identifiers, licensing constraints, and human review. Understanding coverage is necessary before making valuation or report-quality claims.
- Consequences: Future work may include source inventories, field coverage matrices, valuation-confidence rubrics, and data coverage reports. This workstream should not require real client data in ordinary design or demo batches.

## Decision 0007: Arangur Analyzes Portfolio Impact Under Assumptions, Not Market Forecasts

- Date: 2026-06-27.
- Decision: Arangur should distinguish portfolio-impact analysis under stated assumptions from market forecasting.
- Reason: Forecasting claims would require a different methodology, validation burden, compliance posture, and caveat language than the current product direction.
- Consequences: Scenario language should focus on "under these assumptions" and avoid prediction claims. External scenario sources should be treated as assumption providers, not as proof of future outcomes.

## Decision 0008: Practicum Research Should Focus On Coverage, Cleansing, And Feasibility

- Date: 2026-06-27.
- Decision: Data-availability or practicum-style work should focus on source coverage, available fields, identifiers, cleansing, reconciliation, and valuation feasibility rather than predictions.
- Reason: This research can directly inform MVP feasibility and report confidence without crossing into investment forecasting.
- Consequences: Analyst outputs should be domain briefs, source inventories, field dictionaries, feasibility ratings, and synthetic examples for future fixtures.
