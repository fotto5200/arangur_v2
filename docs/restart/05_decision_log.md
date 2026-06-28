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

## Decision 0009: Copy The Education Private-Demo Stack For Arangur's First Deployable Demo

- Date: 2026-06-27.
- Decision: Arangur v2 should reuse the Education private-demo stack shape for the first deployable app.
- Reason: The Education app already has a working FastAPI, Docker Compose, Postgres, Lightsail, Caddy, and Cloudflare private-demo pattern.
- Consequences: Arangur should design its first deployable demo around a FastAPI backend, backend-served browser UI, internal Postgres, protected admin/report surfaces, demo seed path, and Lightsail/Caddy/Cloudflare deployment. See `docs/decisions/0002_copy_education_private_demo_stack.md`.

## Decision 0010: UI Leads With Client Question

- Date: 2026-06-28.
- Decision: The outward-facing Arangur UI should lead with `Client question`.
- Reason: Arangur is a portfolio communication system. The advisor needs to begin with the client conversation, not with source selection, workflow names, or analytics modules.
- Consequences: The current source/workflow/run console is technically useful but transitional. Future UI work should redesign the first screen around client questions and briefing preparation.

## Decision 0011: Default Audience Mode Is Standard Family Office Meeting

- Date: 2026-06-28.
- Decision: The default first-demo audience depth mode should be `Standard Family Office Meeting`.
- Reason: This mode balances plain-English client conversation with enough evidence, caveats, and drill-down for a serious family office review.
- Consequences: Executive, analytical stakeholder, and advisor/internal modes remain important, but first-demo UI and reports should default to the standard meeting depth.

## Decision 0012: First Demo Briefing Paths Include Manager 5 Role Review

- Date: 2026-06-28.
- Decision: The first briefing paths should include `Why do we own Manager 5?`.
- Reason: Manager-role explanation is central to communicating multi-manager portfolios and exposes whether managers are differentiated or unintentionally duplicative.
- Consequences: The next UI/reporting work should support this path alongside `Are we on track?`, `Where are we too concentrated?`, `What could hurt us?`, and `What needs verification?`.

## Decision 0013: Workflows Are Internal; Briefing Stories Are External

- Date: 2026-06-28.
- Decision: Workflow labels are internal execution concepts, while briefing stories and client questions are the preferred outward-facing product metaphor.
- Reason: Workflow names help implementation and testing, but advisors and clients think in conversation questions.
- Consequences: UI and reports should map client questions to internal workflows behind the scenes rather than exposing workflow selection as the primary control.

## Decision 0014: Manager Role Review Flags Shadowed Mandates For Advisor Review

- Date: 2026-06-28.
- Decision: Manager-role review should compare manager exposures against agreed client/advisor categories, themes, macro concerns, or mandates and flag duplicated or shadowed roles for advisor review.
- Reason: If one manager closely shadows another across the categories that matter, the advisor needs to ask whether the duplication is intentional or accidental.
- Consequences: Arangur should not automatically recommend removing a manager. It should raise a mandate/role question and provide evidence for advisor-approved interpretation.

## Decision 0015: Target UI Is A Guided Briefing Builder

- Date: 2026-06-28.
- Decision: The target Arangur UI is a guided briefing builder, not a briefing console.
- Reason: A console can expose capabilities, but Arangur's product job is to guide an advisor through composing the right client conversation.
- Consequences: Future UI work should introduce one clear choice at a time, preserve prior choices in a compact summary, and reveal evidence only after the briefing frame is formed.

## Decision 0016: First Screen Shows One Clear Decision

- Date: 2026-06-28.
- Decision: The first screen should show one clear decision, beginning with `Client question`, not every available report, control, artifact, caveat, or history item.
- Reason: Showing every requirement at once makes the product feel like a reporting console or brokerage dashboard instead of a guided briefing builder.
- Consequences: Audience depth, source context, evidence bundle, report links, recent run history, and technical details should appear only in later steps or appendices.

## Decision 0017: Client Briefing And Advisor Builder Are Separate Surfaces

- Date: 2026-06-28.
- Decision: The advisor guided builder and client briefing page should be separate surfaces.
- Reason: Advisors need preparation, draft, caveat, and evidence controls; clients need an answer-first briefing with minimal supporting cards and responsible confidence language.
- Consequences: The builder should compose and approve the briefing. The client page should show title/family name, client question, plain-English answer, three to five cards, compact confidence note, and optional appendix buttons.

## Decision 0018: Technical Artifacts Belong In Technical/Admin Appendix

- Date: 2026-06-28.
- Decision: Technical artifacts and JSON/report links should be hidden in a technical/admin appendix, not the main advisor or client path.
- Reason: Workflow IDs, run IDs, artifact paths, JSON links, report package links, and local report indexes are useful for validation and administration but distract from briefing composition.
- Consequences: The main guided path should avoid raw report links, JSON links, report packages, implementation roadmaps, and full technical details. A protected or clearly labeled admin/report browser can retain them.

## Decision 0019: Dense Briefing Console Is Transitional

- Date: 2026-06-28.
- Decision: The current dense browser briefing console is transitional and should be redesigned.
- Reason: It proves that client-question mapping and report artifacts can work in the browser, but it presents too much at once and should not define the long-term product interaction.
- Consequences: The next UI implementation batch should replace the dense console with a sparse guided builder before adding deeper UI polish, backend metadata, or client-facing briefing surfaces.
