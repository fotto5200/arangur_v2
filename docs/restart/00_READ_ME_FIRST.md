# Arangur v2 Restart Docs

This directory is the first place a new ChatGPT strategy thread or Codex implementation restart should read. Read these files in numeric order before proposing strategy or changing code.

The restart docs are ordered context files, not conventional after-the-fact documentation. Their job is to preserve the current project shape, decisions, active workstreams, stop conditions, and next safe actions so the project can restart cleanly after a context reset.

## Role Split

- Frank is the product owner. Frank owns product direction, business judgment, and final calls on strategy.
- ChatGPT is the strategic planner and controller thread. It should translate Frank's goals into bounded implementation batches, keep the product direction coherent, and decide when a decision needs Frank.
- Codex is the implementation and repo agent. Codex should receive bounded work packages, inspect the repo, make scoped changes, run relevant checks, and report results.

Codex should not need routine yes/no approval for ordinary technical work inside an authorized batch. It should stop only when a stop condition is reached, when scope is unclear in a risky way, or when product strategy rather than implementation judgment is required.

## Current Product Direction

Arangur v2 should begin with a thin end-to-end demo system:

simple local demo data -> canonical portfolio snapshot -> market data fixture -> simple valuation -> exposure / overlap summary -> simple scenario shock -> generated advisor-readable report or viewer

Plaid ingestion is expected to come early, but it is not the first organizing step. Plaid should become one ingestion adapter that produces the same canonical portfolio snapshot as the simple demo data loader.

The legacy MATLAB project is read-only reference material until a specific MATLAB audit batch is authorized. It should not be treated as the organizing center for v2.

The current priority is a stable, replaceable, thin demo path with clear component boundaries.
