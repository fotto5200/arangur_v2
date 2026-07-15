# Arranger UI Design Inputs Digest v1

Status: external design-lab and Work-derived input consolidation, 2026-07-15

## 1. UI design-lab inventory summary

Active design-lab directory: `C:/Users/fotto/cursor/Arangur UI Design Lab`

Secondary directory found: `C:/Users/fotto/Documents/Arangur UI Design Lab` (empty at discovery time)

- Markdown files: 8, all fully read.
- HTML files: 2, both source-inspected and indexed; neither was rendered or modified.
- Major themes: user-job-first design, one dominant action, progressive disclosure, immutable dated briefings, template-versus-briefing separation, evidence-in-context, client objective reporting, stable scenario comparison, advisor-versus-manager responsibility, and report-family-specific visualization.
- Design approaches found: three application architectures; three client-report storytelling directions; three visual concepts inside the selected story; manager drill-down refinement; and a five-family report breadth test.
- Prototypes found: one three-step Objective Horizon/manager drill-down prototype and one multi-report breadth-test prototype.

The lab is newer than most repo UI notes (lab files dated 2026-07-13 versus many repo UI notes dated 2026-06-27 to 2026-06-29), but it is external design input, not repo-canonical product state.

## 2. Extracted UI requirements

### Advisor entry and workflow

- Begin from the user's objective/job, not the current screen layout or internal report taxonomy.
- Use a workflow-first or job-first advisor entry that asks what conversation, briefing, or review is needed.
- Let the advisor choose a conversation type without exposing workflow IDs, run IDs, schemas, artifact paths, or generation machinery.
- Provide workflow templates/reusable briefing templates and a clear “use current data” path.
- Support custom workflow/template creation only through meaningful business concepts: audience, purpose, ordered sections/report views, emphasis, exclusions, and visibility.
- Keep one primary job and one dominant action per focused state.

### Builder versus presenter

- Advisor builder/review can expose composition, order, caveats, visibility, and evidence.
- Client presenter must be a separate, clean state with fixed as-of date, conclusions first, one dominant Next action, and no generation/edit/admin controls.
- Client preview should render the advisor-selected sequence rather than a generic static page.
- Advisor view and client preview may share evidence but must not share the same density or controls.
- Evidence opens from a specific claim and returns to the exact claim/position.

### Report journey and depth

- Use the shared depth path: Understand → Explain → Verify → return to the same conclusion.
- Show useful output before construction machinery.
- Use progressive disclosure by default.
- Keep tables and exact calculations at verification depth unless exact cross-row/column comparison is itself the job (notably attribution).
- Preserve ordered report/briefing journey and historical immutability.

### Report selection and visibility

- Allow report selection and ordering in the advisor surface.
- Support client-facing, advisor-only, appendix, and gated/deferred states.
- Show gated/deferred items as unavailable pending data/method/approval; do not fabricate.
- Avoid raw artifact names and generated filenames in ordinary UI.
- External manager story workflow must show translation/non-endorsement, candidate status, and approval gates before any client use.

### Clean/simplified UI

- Every visible panel, card, label, and control must justify its presence.
- Prefer fewer, larger decisions over many configuration steps.
- Hide advanced, administrative, and technical controls until requested.
- Remove meta-labels when the interface can communicate the action directly.
- Do not create a new product object without a clear user-facing lifecycle.
- Keep scenario bases, scales, and horizons stable when comparisons are intended.

## 3. Alternative UI approaches

### Application interaction architectures

| Approach | Concept | Strengths | Weaknesses | Likely status |
| --- | --- | --- | --- | --- |
| The Briefing Desk | Finished dated briefing is the center of gravity; creation, history, alignment, and evidence are entered from document context. | Strongest reading/presentation flow; trustworthy historical identity; evidence anchors naturally. | Alignment and portfolio switching may feel secondary; document can become a dumping ground. | Candidate; needs Frank review. |
| The Arangur Guide | User states an objective in business language and the guide asks only consequential questions. | Fastest for users who know the outcome but not the object; hides system structure; handles ambiguity naturally. | Interpretation risk, repeated clarification, conversation clutter, and discoverability concerns. | Candidate; needs Frank review. |
| The Investment Library | Durable Briefings, Templates, and Portfolios are top-level collections with focused object lifecycles. | Strong retrieval, history, ownership, and template/briefing distinction. | Can become a filing system/dashboard; cross-object jobs may fragment; metadata can crowd content. | Candidate; needs Frank review. |

The lab explicitly says not to combine these before selection.

### Client-report storytelling directions

| Approach | Concept | Strengths | Weaknesses | Likely status |
| --- | --- | --- | --- | --- |
| The Plan Check | Organize around the two or three client objectives that define success: Return, Capital Growth, Cash Support, Resilience. | Directly answers “How am I doing?”; strong recurring review structure; exceptions stay prominent. | Can devolve into a scorecard; depends on real objectives and boundaries. | Selected for visual exploration; provisional until inputs/prototype pass. |
| The Wealth Journey | Explain opening value, flows, ending value, and forward paths through time. | Excellent capital/cash reconciliation and natural motion. | Requires reliable flow history; can imply false forecast precision or bury objective status. | Non-selected comparison/reference direction. |
| The Stewardship Brief | Explain client outcome, advisor decisions, manager implementation, and forward action. | Strong accountability and sophisticated governance story. | Can feel self-serving or overly technical. | Non-selected comparison/reference direction. |

### Visual concepts within Plan Check

| Concept | Premise | Strengths | Risks | Likely status |
| --- | --- | --- | --- | --- |
| Objective Horizon | Aligned actual-versus-objective/boundary measures with favorable-right/unfavorable-left semantics. | Fast status scan; direct labels; works with client-selected objectives. | KPI-rail effect; normalization may imply comparability; too many objectives break it. | Preferred for refinement, not frozen. |
| Capital Landscape | Continuous capital path from opening value through change to current value and forward scenarios. | Clearest capital reconciliation and meaningful animation. | False precision; can revert to rejected journey-first narrative. | Candidate/reference. |
| Editorial Focus | One declarative sentence and one visual relationship per state. | Calmest five-minute presentation; strongest immediate comprehension. | More steps; can oversimplify for sophisticated clients. | Candidate/reference. |

## 4. HTML prototype digest

### `arangur_objective_horizon_manager_refinement_v1.html`

- Title: **Arangur Objective Horizon Manager Refinement**.
- Type: self-contained interactive static visual prototype inside a sandboxed `iframe`/`srcdoc`; not a generated report and not production app code.
- Apparent screen/prototype: a three-step client presentation/refinement sequence.
- Major sections/components:
  - Portfolio Horizon: “Growth is ahead of plan. One risk is outside the review boundary.”
  - Manager contribution horizon: manager contributions and a +1.05 percentage-point combined manager result.
  - Selected manager horizon: manager mandate performance, portfolio contribution, and allocation-to-role.
  - Manager selector for Managers A–F.
  - Explain responsibility, Verify manager evidence, Previous/Next controls, and step progress.
- Workflow/use case: Plan Check client presentation with portfolio-to-manager contextual drill-down.
- Implementation relevance: strong input for client-report presentation, stable semantic direction, manager responsibility language, and contextual drill-down.
- Caveats: uses design-only objectives/tolerances; does not settle application navigation, data lifecycle, accessibility testing, or a global report visual system.

### `arangur_report_breadth_test_v1.html`

- Title: **Arangur Report Breadth Test v1**.
- Type: self-contained interactive static prototype/design experiment; not a generated production report.
- Apparent screen/prototype: a selector across five report families, each with an opening and explain state.
- Major sections/components:
  - Cash Support: required versus projected cash and a cash bridge.
  - Scenario Risk: deterministic point, sensitivity range, and probability range with explicit semantic separation.
  - AI Lens: portfolio composition and manager-by-lens explanation.
  - Advisor Attribution: manager rows and selected-mandate/target-weighting/funding-drift effects.
  - Manager Attribution: selected-manager benchmark/sleeve rows and benchmark/security decision decomposition.
  - Previous/Next/progress controls and exact tables for the attribution specimens.
- Workflow/use case: cross-report visual-language validation, not one end-to-end advisor workflow.
- Implementation relevance: shows which rules are system-wide versus report-family-specific and protects the separate denominators of advisor and manager attribution.
- Caveats: within-manager fixture is illustrative; the global visual system is explicitly not frozen; probabilistic values are design-only where the repo has no approved range engine.

## 5. Integration recommendations

### Advisor Workflow UI Integration Blueprint v1

Bring forward:

- the six user jobs and minimum-success outcomes;
- immutable briefing/template distinction;
- one dominant action and progressive disclosure;
- workflow/job-first entry without internal identifiers;
- advisor builder versus client presenter separation;
- evidence-in-context and exact return path;
- the three application architectures as an explicit Frank decision, not an implicit hybrid;
- the four canonical repo workflows and their accepted/gated step metadata;
- a vocabulary reconciliation between workflow, template, briefing, report view, and generated report.

### Advisor Workflow UI Wiring v1

Implement only after the blueprint is approved:

- selected first screen/workflow chooser;
- workflow/template reuse and creation scope;
- ordered report journey with visibility/gate states;
- advisor review and client preview/presentation modes;
- external-story caveats and approvals;
- hidden Developer / QA artifact layer;
- no raw artifact filenames in ordinary paths.

### Later demo/deployment polish

- refine Objective Horizon only for accepted client-report states;
- preserve static/reduced-motion equivalents;
- test the five breadth-test report families;
- run realistic scripts for five-minute client, sophisticated evidence request, scenario comparison, cash concern, and historical integrity;
- perform local Docker browser rehearsal before any fresh deployment task.

## 6. Items requiring Frank review

1. Choose Briefing Desk, Arangur Guide, Investment Library, or explicitly authorize a tested hybrid after comparing the six jobs.
2. Decide final advisor-facing vocabulary: workflow, briefing template, briefing, report view, and generated report.
3. Confirm whether the four repo workflow families are the first product choices and whether External Manager Story Translation stays advisor/internal.
4. Confirm which design-lab stage gates are mandatory before the next local UI implementation.
5. Approve, revise, or reject Objective Horizon after reviewing manager responsibility and breadth-test behavior.
6. Decide how client objectives/thresholds are sourced; the current 6.5%, 4.0%, ±3.0 pp, and -15% values are illustrative only.
7. Decide whether historical briefings become durable backend objects now or remain a later persistence tranche.
8. Decide how much exact attribution detail is client-accessible versus advisor/committee-only.
