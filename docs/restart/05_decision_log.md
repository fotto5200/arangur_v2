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
