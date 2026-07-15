# Arranger Project Control Dossier v1

Status: documentation-discovery handoff

Prepared: 2026-07-15

Primary audience: Frank, ChatGPT strategy/controller threads, and future Codex implementation tranches

## 1. Executive summary

Arranger is becoming a workflow-based advisor/client reporting product backed by an internal analytics control plane. The repository already contains a working synthetic local demo, a browser-local advisor workflow/report lifecycle, four canonical report workflows, accepted report-family classifications, extensive generated report mockups, a full-revaluation scenario foundation, and a carefully separated attribution architecture. Report design and workflow catalog work are substantially advanced.

The likely next product phase is not more report math. It is controlled UI integration: reconcile the committed workflow catalog, the current advisor app, and the newer external UI design-lab work into one canonical implementation blueprint before modifying the product surface. The most important project-control risk is that knowledge is distributed across committed repo docs, generated mockups and JSON artifacts, restart documents, Codex commits, ChatGPT/Work outputs, and the external Arangur UI Design Lab.

The repository should become the durable source of truth. This dossier and its companion inventory, decision register, UI digest, and integration queue provide the first consolidated control layer.

## 2. Product identity

Arranger/Arangur is a portfolio communication, reporting, and analytics-control product for advisors, family offices, investment committees, and sophisticated clients. It turns portfolio evidence into an ordered conversation: what the portfolio owns, whether it supports the client's plan, what decisions drove results, what risks matter, and what should be reviewed next.

Its product stance is that analytics support the briefing rather than dictate the interface. Complex valuation, scenario, attribution, classification, and confidence machinery belongs behind simple client questions and advisor-controlled workflows. The durable operating principle is: AI may propose, Arranger computes, and the advisor approves.

## 3. Four major surfaces

### Advisor workflow surface

- Purpose: let an advisor choose a conversation, compose or reuse an ordered workflow, populate it with a dated data snapshot, review it, and present the resulting briefing.
- Users: advisors, relationship managers, CIOs, investment teams, and client-service staff.
- Current repo support: a dependency-free browser app with Advisor Home; four top-level actions (create, open, populate, present); browser-local named workflows; a catalog-driven report-element composer; client/advisor sets; preview; demo population; browser-local generated-report shelf; and Developer / QA separation. The four new audience workflows also exist as committed JSON, but are not yet the canonical Advisor Home chooser.
- Not yet built: canonical workflow-catalog integration into the current UI; an approved application-level interaction architecture; durable generated-report history; production workflow persistence; a reconciled template/briefing/report vocabulary; and a final UI implementation contract based on the design lab.
- Risks: mixing old composer concepts with new workflow concepts, exposing raw artifact names, over-configuring the first screen, confusing templates with generated briefings, and implementing a design-lab candidate before Frank approves it.

### Client reporting surface

- Purpose: present a dated, client-ready, advisor-approved narrative with conclusions first, evidence on demand, and technical machinery hidden.
- Users: principals, family-office members, sophisticated clients, investment committees, and advisor presenters.
- Current repo support: client and advisor preview models; generated HTML/Markdown fragments; briefing-set preview fixtures; generated report artifacts; accepted report mockups; and a working browser presentation view for local synthetic artifacts.
- Not yet built: the final client presentation system implied by the external design lab; an immutable historical briefing library backed by durable storage; validated client objectives and plan thresholds; production export/share behavior; and production/client-ready data.
- Risks: treating positive performance as “on plan” without client objectives, mixing deterministic scenarios with probability ranges, overloading the client view with attribution detail, and allowing setup/export/admin controls into presentation.

### Private client-data execution layer

- Purpose: ingest and process client holdings while minimizing unnecessary Arranger visibility into private client information.
- Users: advisory firms, operations teams, data custodians, and authorized administrators; ordinary clients and advisors should experience only governed outputs.
- Current repo support: source-neutral portfolio contracts, Plaid-shaped mock ingestion, synthetic fixtures, optional Postgres skeletons, local Docker/private-demo packaging, and explicit no-real-data boundaries.
- Not yet built: production custody/Plaid adapters, tenant isolation, entitlements, encryption/key management, audit/retention policy, private execution topology, and a formal minimization architecture for what data leaves the client-controlled environment.
- Risks: premature use of real holdings, leaking identifiers through artifacts or logs, confusing local-demo persistence with production privacy, and designing this layer after UI assumptions have already hardened.

### Arranger internal analytics control plane

- Purpose: curate, validate, approve, and publish analytic packs containing themes, lenses, scenarios, shocks, confidence rules, valuation coverage, and report capabilities for the advisor app to consume.
- Users: internal analytics, investment/research, model governance, and QA teams—not ordinary advisors or clients.
- Current repo support: a documented publish/consume boundary, an analytic-pack contract, a synthetic demo pack, full-revaluation architecture, scenario-basis and lens-mapping designs, valuation coverage mapping, calculated attribution engines, and committed proof outputs.
- Not yet built: an internal studio/control-plane UI, production governance workflows, live data/market inputs, production pricing coverage, approval/version lifecycle, and operational publishing controls.
- Risks: exposing construction controls in the advisor app, treating synthetic packs as recommendations, allowing unapproved proxies or methodologies into client reporting, and building the internal studio before the advisor workflow direction is settled.

## 4. Current accepted workflow families

### Principal / Family Office Briefing

- Audience: principal or family-office member; minimal client briefing.
- Core question: where are we, is cash/spending supported, what is the largest risk, what should we watch, and what is the advisor planning to do?
- Ordered flow: Portfolio Representation Status → Cash Flow Delivered → Cash-Flow Support Outlook → Coverage and Confidence Warning (advisor-supporting) → Aggregated Asset Allocation → Current Portfolio Scenario Downside → gated High-Level Advisor Plan / Next-Year Positioning.
- Sources: `docs/product/report_workflow_catalog_v1.md`, `data/simulation/report_workflows/demo_workflows_v1/principal_family_office_briefing_minimal_v1.json`, and the related revaluation v2 mockups.
- UI gaps: translate setup/readiness into an unobtrusive gate; keep the opening client-focused; define how the future advisor plan handoff appears without inventing a recommendation.

### Engaged Client / Investment Committee Review

- Audience: engaged client, family investment committee, or sophisticated principal.
- Core question: how did policy, managers, exposures, themes, and scenarios explain the portfolio?
- Ordered flow: Portfolio Representation Status → Policy Allocation Review → Advisor Policy Attribution by Manager/Sleeve → Manager Mandate Attribution Summary → Full Lens Exposure (AI Adoption) → Full Lens Exposure (Energy Security) → Manager by Lens Exposure (AI Adoption) → Current Portfolio Scenario Downside → optional Manager Driver Attribution Matrix.
- Sources: the workflow catalog and `engaged_client_investment_committee_review_v1.json`, policy allocation/attribution mockups, manager attribution mockups, and revaluation v2 mockups.
- UI gaps: progressively disclose the advisor-review steps, keep the dense manager matrix optional, and preserve exact denominator/basis language when attribution is opened.

### Advisor / Manager Oversight

- Audience: advisor and internal investment team.
- Core question: which mandates, managers, implementation effects, drift items, and coverage flags require attention before a client conversation?
- Ordered flow: Policy Allocation Drift Summary → Manager Mandate Benchmark Basis → Advisor Policy Attribution → Manager Mandate Attribution Summary → Manager Driver Attribution Matrix → Within-Manager Attribution Detail → Manager Implementation Handoff → Coverage and Confidence Warning → gated Coverage/Confidence by Manager.
- Sources: `advisor_manager_oversight_v1.json`, policy allocation v1, policy attribution v2, and manager attribution v1 artifacts.
- UI gaps: exception-first navigation, a clear manager drill-down return path, and separation of oversight evidence from client presentation.

### External Manager Story Translation

- Audience: advisor, investment committee, or manager-facing discussion; not client-facing until reviewed.
- Core question: how should an outside manager worldview be translated into lenses, key-price scenarios, candidate proxies, workflow gates, and governance caveats without endorsement?
- Ordered flow: Manager Story Summary → Implied Lenses → Key-Price Scenario Set → Candidate Benchmark/Proxy Map → gated Portfolio Through External Lens → gated Manager by External Lens → gated Scenario Downside under External Story → gated Scenario by Lens → Governance/Caveat Note.
- Sources: `docs/product/external_manager_story_workflow_v1.md`, the external-story workflow JSON, and the seven-artifact translation pack.
- UI gaps: make translation/non-endorsement unmistakable, show gates before report promises, keep candidate proxies internal until approved, and decide whether the first UI exposure is advisor-only.

## 5. Current accepted report families

- Portfolio/cash-flow/status: Portfolio Representation Status, Cash Flow Delivered, Cash-Flow Support Outlook, Aggregated Asset Allocation, Allocation by Manager, Coverage and Confidence Warning, and focused concentration variants.
- Scenario/lens/exposure: Current Portfolio Scenario Downside, Full Lens Exposure, Manager by Lens Exposure, and consistent-category concentration. Scenario-by-lens and benchmark/range comparisons remain gated or design-soon.
- Policy allocation: Policy Allocation Review is primary; Policy Allocation Drift Summary is advisor-only; Imputed Current Allocation Baseline and Manager Mandate Benchmark Basis are setup/readiness artifacts.
- Advisor policy attribution: Advisor Policy Attribution by Manager/Sleeve is the accepted primary surface; Advisor Policy Effect Totals is supporting. Policy-Level Attribution Summary v1 remains calculation/reference material and is superseded as the primary product surface.
- Manager mandate attribution: Manager Mandate Attribution Summary is primary; Manager Driver Attribution Matrix is the accepted all-manager component dialogue; Within-Manager Attribution Detail is advisor-only; Manager Implementation Handoff is diagnostic/control.
- External manager story translation: story summary, implied lenses, key-price scenarios, proxy candidates, gated report map, and governance note. These are translation artifacts, not endorsed investment reports.

## 6. Attribution architecture

Advisor policy attribution and manager attribution are separate responsibility layers.

The advisor layer evaluates decisions made before manager implementation:

- Selected mandate effect: the neutral selected-mandate basket versus the global benchmark.
- Target weighting effect: target policy weights versus neutral selected-mandate weights.
- Funding drift effect: actual funding weights versus target weights.
- Advisor policy effect: the sum of those effects before manager implementation.

The manager layer evaluates implementation inside assigned capital and mandate:

- Manager mandate effect: manager return versus the approved manager mandate benchmark, expressed on the defined manager or portfolio-effect basis.
- Manager Driver Attribution Matrix: all six managers plus total, decomposed into mandate sub-benchmark selection, mandate sub-benchmark sizing, asset selection, asset sizing, and residual/unexplained.
- Within-manager detail: selected-manager drill-down from the matrix.
- Handoff: manager implementation reconciles back to the advisor policy layer without blending accountability.

The older Policy-Level Attribution Summary v1 bridge remains useful as a local calculation reference but is superseded as the primary product-review surface. Equal-weight attribution remains diagnostic unless an explicit policy says otherwise. Blended/all-in attribution, timing, dollar P&L, position-level attribution, and production/client attribution remain deferred or gated.

## 7. UI design state

### Repo-canonical UI state

Committed repo documents define a workflow/briefing philosophy, a briefing-set builder model, client versus advisor surfaces, an information budget, and the current browser composer/report lifecycle. The committed app is operational for synthetic local demos and is more current than several older UI notes. Canonical workflow JSON exists, but it has not yet been reconciled into the current Advisor Home and composer vocabulary.

### External Work/design-lab inputs

The active external lab at `C:/Users/fotto/cursor/Arangur UI Design Lab` contains eight Markdown design artifacts and two self-contained interactive HTML prototypes. It defines six user jobs, three independent application interaction architectures, a client-report communication contract, three client storytelling directions, a selected report story, visual concept alternatives, manager refinement, and a five-family breadth test.

### Candidate UI ideas

- Application architectures: The Briefing Desk, The Arangur Guide, and The Investment Library. None is selected.
- Client-report storytelling: The Plan Check is selected; The Wealth Journey and The Stewardship Brief remain comparison/reference directions.
- Visual concepts inside Plan Check: Objective Horizon is preferred for continued refinement; Capital Landscape and Editorial Focus remain candidates/reference concepts.
- Shared reporting language: conclusion first; Understand → Explain → Verify → return; stable semantics; direct labels; one dominant action; tables at verification depth or when exact comparison is the task.

### Accepted direction versus unresolved choices

Accepted for the client report narrative: The Plan Check. Preferred but not frozen: Objective Horizon. Not accepted at the application level: any of the three interaction architectures. Not frozen: a global visual system, production navigation, template/briefing lifecycle UI, or the final advisor workflow builder form.

### Items needing Frank review

- Select or reject an application-level architecture.
- Confirm whether the current repo term “workflow” remains advisor-facing or becomes template/briefing language.
- Reconcile the repo's workflow-first direction with the lab's warning against exposing workflow terminology.
- Decide whether External Manager Story Translation is advisor/internal only in the first release.
- Approve the Objective Horizon refinement and breadth-test rules before treating them as implementation requirements.
- Decide which design-lab stage gates are required for the next private demo versus later production polish.

## 8. What is source of truth

- Committed repo docs, contracts, JSON catalogs, accepted mockups, and code should become the source of truth.
- ChatGPT, Work, and Codex threads are input channels and decision-making venues, not durable product memory.
- External UI design-lab files are design inputs until accepted decisions and implementation contracts are integrated into the repo.
- Generated artifacts are evidence of current capabilities and accepted product-review shapes; they do not automatically define the UI.
- Where restart docs conflict with newer committed product behavior, the current code/contracts and newest dated docs should win, with the discrepancy recorded rather than silently blended.

## 9. Immediate next phase

Recommended next tranche: **Advisor Workflow UI Integration Blueprint v1**.

Its job is to reconcile the four canonical workflow families, current advisor app behavior, accepted report classifications, and external design-lab inputs into one repo-canonical interaction blueprint and implementation contract. It should make the unresolved product choices explicit before code changes.

Then proceed in order:

1. **Advisor Workflow UI Wiring v1** — implement the approved workflow chooser, builder/reuse path, review/client preview separation, and gated/deferred behavior.
2. **Local Docker/private-demo polish** — run the approved journey locally, fix only observed product/readiness issues, and preserve synthetic/private boundaries.
3. **Fresh deployment thread for AWS/private demo** — use a new, deployment-scoped task after local acceptance; do not mix deployment decisions into UI design work.

## 10. Risks and open questions

- Distributed knowledge: the same topic is split across repo docs, generated artifacts, restart history, commits, and external design-lab files.
- UI overcomplexity: report capability can easily become visible controls, cards, or tables that the current task does not require.
- Premature deployment: the local stack is ready enough for rehearsal, but product direction and security/privacy boundaries are not production-ready.
- Privacy/data boundary: the private client-data execution architecture remains conceptual and must precede real holdings.
- Internal analytics control plane: required future surface, but not the next UI build and never an advisor-facing construction panel.
- Unresolved application architecture: Briefing Desk, Arangur Guide, and Investment Library remain alternatives.
- Vocabulary conflict: the repo uses workflows and report elements; the lab prefers briefings, briefing templates, alignment reviews, and evidence while hiding technical workflow language.
- Raw artifact clutter: JSON paths, report package links, run IDs, mockup filenames, and internal statuses must remain in Developer / QA or evidence/admin layers.
- Client objective gap: design-only return/growth/risk thresholds must never be mistaken for supplied client facts.
- Historical integrity: generated briefings should become immutable dated objects; “use current data” must create a new briefing rather than mutate history.
