# Advisor Workflow UI Integration Blueprint v1

Status: **approved by Frank and locally implemented** in `Advisor Workflow UI Wiring v1`, 2026-07-15

Prepared: 2026-07-15

## 1. Purpose and status

This blueprint reconciles the current Arangur advisor app, the four committed workflow families, accepted report and attribution architecture, project-control documents, and the Arangur UI Design Lab. It defines the product decisions required before `Advisor Workflow UI Wiring v1`.

This tranche does not implement UI, wire workflows, change analytics, change Docker/deployment, create production persistence, or authorize real data. Recommendations explicitly marked for Frank review remain non-final.

## 2. Source basis

Primary consolidated input: `docs/project_control/ARRANGER_UI_BLUEPRINT_INPUT_PACKET_v1.md`.

Repo-canonical product sources:

- `docs/product/report_workflow_catalog_v1.md`
- `docs/product/demo_report_suite_v1.md`
- `docs/product/report_family_acceptance_status_v1.md`
- `docs/product/external_manager_story_workflow_v1.md`
- `docs/demo/advisor_report_workflows.md`
- `data/simulation/report_workflows/demo_workflows_v1/`

Current app evidence read without modification:

- `src/arangur/app/static/index.html`
- `tests/test_app_health.py`
- `tests/test_app_advisor_workflows.py`
- `tests/test_app_generated_reports_api.py`
- `tests/test_briefing_set_preview.py`
- `tests/test_report_workflow_catalog.py`

Design sources:

- All eight Markdown files and both HTML prototypes in `C:/Users/fotto/cursor/Arangur UI Design Lab/` listed in the input packet.
- `docs/ui_reporting/ui_reporting_philosophy_v1.md`
- `docs/ui_reporting/briefing_set_builder_model_v1.md`
- `docs/ui_reporting/briefing_set_client_preview_model_v1.md`
- `docs/ui_reporting/guided_briefing_builder_correction_v1.md`

Companion contracts created with this blueprint:

- `docs/product/advisor_workflow_ui_application_architecture_v1.md`
- `docs/product/advisor_workflow_ui_vocabulary_lifecycle_contract_v1.md`
- `docs/product/advisor_workflow_ui_state_map_v1.md`
- `docs/product/advisor_workflow_ui_visibility_gating_matrix_v1.md`
- `docs/project_control/ARANGUR_UI_BLUEPRINT_FRANK_REVIEW_ITEMS_v1.md`

## 3. Product name

The canonical product name is **Arangur**. “Arranger” in older notes is a transcription error unless it appears in an existing filename, directory name, commit, or historical artifact. New prose must not propagate the error. Existing `ARRANGER_...` project-control filenames are retained for path stability.

## 4. Current product foundation

### Existing private-demo app

The dependency-free static app currently provides a Briefings home, four built-in briefing templates, browser-local custom templates, a report-element/narrative composer, separate client/advisor sets, preview/export, generated briefing/report artifacts, browser-local generated history, hash routes, backend draft test controls, and Developer / QA tools. It is synthetic/private-demo evidence, not the approved future information architecture. Sources: `src/arangur/app/static/index.html`, `docs/demo/advisor_report_workflows.md`, and `tests/test_app_health.py`.

### Current lifecycle

The implemented lifecycle is `briefing template → generate with current data → generated dated report → open/present`. Four committed workflow JSON definitions are adapted into the same payload model as browser-created templates. Built-ins cannot be overwritten; generated artifacts are saved in the browser-local shelf. Source: `docs/demo/advisor_report_workflows.md`.

### Four workflow definitions

The catalog contains Principal / Family Office Briefing, Engaged Client / Investment Committee Review, Advisor / Manager Oversight, and External Manager Story Translation. The JSON order, report ID, audience visibility, role, status, source, and gate metadata control later wiring. Source: `data/simulation/report_workflows/demo_workflows_v1/report_workflow_catalog_manifest.json` and its four workflow files.

### Accepted report families

Accepted primary groups cover portfolio/cash/status, scenarios/lenses/exposure, policy allocation, Advisor Policy Attribution v2, and manager mandate attribution. Supporting, advisor-only, setup/readiness, diagnostic, gated, and superseded status remains explicit. Source: `docs/product/report_family_acceptance_status_v1.md`.

### Attribution responsibility split

Advisor policy attribution contains selected mandate, target weighting, and funding drift effects before manager implementation. Manager attribution compares actual capital and manager return with the approved mandate benchmark and decomposes manager decisions on an explicit denominator. The layers must not be blended. Equal-weight attribution is diagnostic unless selected as policy; Policy-Level Attribution Summary v1 is superseded as the primary surface. Source: `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`.

### External story translation pack

The pack translates a narrative into story summary, implied lenses, key-price scenario candidates, approval-required proxy candidates, gated report concepts, and governance caveats. It does not verify, endorse, recommend, or produce client-ready investment guidance. Source: `docs/product/external_manager_story_workflow_v1.md` and `data/simulation/external_story_translation/external_manager_story_translation_pack_v1/`.

## 5. Selected application architecture recommendation

### Recommendation

Adopt the named **Conversation Briefing Desk** architecture, **recommended for Frank review and not final until approved**.

It begins with a deterministic business-conversation chooser and makes the dated briefing the center of gravity after generation. It deliberately borrows only:

- business-job framing from Arangur Guide, not a free-form assistant shell;
- dated reading/presentation/evidence behavior from Briefing Desk;
- explicit template/briefing lifecycle and secondary history retrieval from Investment Library, not a library-first dashboard.

Pure Briefing Desk is too document-first for initial preparation and alignment; pure Guide adds interpretation/trust risk; pure Investment Library is object-first when the product thesis is conversation-first. The full comparison and rejected/deferred behaviors are in `docs/product/advisor_workflow_ui_application_architecture_v1.md`.

## 6. First-screen contract

- Heading: **Prepare a briefing**.
- Question: **What conversation are you preparing?**
- Choice-group label: **Briefing types**.
- Choices:
  1. Principal / Family Office Briefing
  2. Engaged Client / Investment Committee Review
  3. Advisor / Manager Oversight
  4. External Manager Story Translation
- Dominant action after selection: **Continue**.
- Secondary action: **Open a prior briefing**.
- Subordinate maintenance action: **Manage templates**.
- Developer / QA is separately entered and not a peer action.

`Briefing type` is the recommended advisor-facing label. `Conversation` is the question framing. `Workflow` remains the internal catalog term. This recommendation requires Frank approval.

## 7. Canonical vocabulary

The complete contract is `docs/product/advisor_workflow_ui_vocabulary_lifecycle_contract_v1.md`.

| Internal term | Advisor-facing term | Client-facing term | Status |
| --- | --- | --- | --- |
| Workflow | Briefing type | Not shown | Recommended; Frank approval required |
| Workflow/saved definition | Briefing template | Not shown | Recommended; Frank approval required |
| Generated report artifact | Briefing | Briefing | Recommended; Frank approval required |
| Client/advisor report set | Briefing sections / Advisor Review sections | Section titles | Recommended |
| Report family/element/view | Section type in bounded editing | Plain-English section title | Accepted recommendation |
| Advisor review | Advisor Review | Not shown | Accepted concept; defaults need approval |
| Client preview | Client Preview | Not shown as a mode | Recommended |
| Presentation | Present / Presentation | No technical mode label | Accepted |
| Evidence | Explain / Verify | Explain / Evidence | Accepted |
| Gated/deferred | Not ready + reason | Hidden unless materially caveated | Accepted |
| Diagnostic | Advisor diagnostic | Hidden | Accepted |
| Setup/readiness | Preparation note / Needs review | Hidden or adjacent material caveat | Accepted |

Avoid workflow IDs, run/job/pipeline language, JSON, schemas, prompts/models/agents, artifact paths, renderer/component terminology, and internal status codes in ordinary UI.

## 8. Object lifecycle

V1 exposes two saved objects:

1. **Briefing template** — reusable definition of audience, purpose, ordered sections, visibility, optionality, and fixed caveats.
2. **Briefing** — generated output fixed to generated and data-as-of dates.

Advisor Review, Client Preview, Presentation, Evidence, and Historical Reading are states, not additional saved objects.

Rules:

- “Create briefing with current data” always creates a new dated briefing.
- Generated briefings are immutable; corrections or current data create a new object.
- Built-in templates are read-only; editing begins a copy saved as a custom template.
- Client Preview does not create or edit an object.
- Presentation changes controls, not content.
- Evidence is bound to the briefing snapshot and originating claim.
- Historical reading never silently refreshes.
- Browser-local demo history may remain during UI wiring; durable production history, tenancy, retention, and audit are a later approved tranche.

## 9. Screen/state map

The binding detailed map is `docs/product/advisor_workflow_ui_state_map_v1.md`.

| State | User job | Dominant action |
| --- | --- | --- |
| Home / Conversation Chooser | Choose the conversation or reopen history. | Continue |
| Template Selection | Choose the approved reusable definition. | Use template |
| Builder | Modify a bounded reusable template. | Preview template |
| Template Preview | Confirm reusable intent, not live output. | Save template |
| Briefing Configuration | Confirm portfolio/audience/date/readiness. | Create briefing with current data |
| Advisor Review | Approve visibility, caveats, and evidence. | Preview for client / Complete review |
| Client Preview | Rehearse exact client content. | Present |
| Presentation | Deliver the ordered conversation. | Next |
| Explain / Verify | Explain or prove one claim. | Verify / Back to conclusion |
| Historical Items/Reading | Reopen an immutable dated briefing. | Open briefing |
| External Story Review | Review translation and gates without endorsement. | Review next translation item |
| Developer / QA | Inspect technical evidence. | Task-specific, separately entered |

Each state contract specifies visible/hidden content, inputs, outputs, transitions, acceptance criteria, and common failure modes. No implementation agent may invent another user-facing saved object or primary state without product review.

## 10. Workflow contracts

The exact step-by-step binding matrix is `docs/product/advisor_workflow_ui_visibility_gating_matrix_v1.md`.

### Principal / Family Office Briefing

- Purpose: smallest useful client conversation about status, cash, broad ownership, downside, and next-year plan.
- Entry label: **Principal / Family Office Briefing**.
- Journey: Representation → Cash Delivered → Cash Outlook → advisor coverage review → Allocation → Scenario Downside → gated Advisor Plan.
- Client surface: all except standalone coverage warning; advisor plan remains gated.
- Hide: dense attribution, coverage machinery, fabricated positioning.

### Engaged Client / Investment Committee Review

- Purpose: allocation, responsibility, lens exposure, and downside for a sophisticated audience.
- Entry label: **Engaged Client / Investment Committee Review**.
- Journey: Representation → Policy Allocation → Advisor Attribution → Manager Attribution → AI Lens → Energy Lens → Manager by AI Lens → Scenario Downside → optional Driver Matrix.
- Advisor-review defaults: both attribution summaries, manager-by-lens, and dense matrix.
- Hide: internal diligence unless approved; exact denominators remain explicit at evidence/table depth.

### Advisor / Manager Oversight

- Purpose: exception-first mandate, allocation, implementation, coverage, and handoff review before client conversations.
- Entry label: **Advisor / Manager Oversight**.
- Journey: Drift → Benchmark Basis → Advisor Attribution → Manager Attribution → Driver Matrix → Selected Manager → Handoff → Coverage Warning → gated Manager Coverage.
- Advisor-only by default; no client preview is created without a separate approved client briefing.
- Hide from client: diagnostics, handoff, readiness, raw coverage, full manager roster when aligned.

### External Manager Story Translation

- Purpose: translate an external worldview into governed questions without endorsing it.
- Entry label: **External Manager Story Translation**.
- Journey: Story → Implied Lenses → Key-Price Scenarios → internal Proxy Candidates → four gated analytic outputs → Governance Note.
- Advisor/internal default in v1.
- Hide: proxy candidates except authorized review and all unavailable analytic outputs from client surfaces.
- Persistent caveat: translated, not verified, not endorsed, not a recommendation; proxies require approval.

## 11. Advisor Review versus Client Preview

- Advisor Review may show caveats, gate reasons, diagnostics, setup/readiness, optional steps, evidence, internal notes, and client-visibility controls.
- Client Preview is the exact ordered content the client would see; it excludes advisor-only, setup, diagnostic, and internal-control material.
- Presentation contains the same content/order as Client Preview with authoring, generation, template, export, admin, and Developer / QA controls removed.
- Client Preview and Presentation remain separate states because rehearsal/approval and audience delivery are different jobs.
- Advisor-only workflows complete in Advisor Review or an advisor/internal presentation; they do not automatically create client content.

## 12. Evidence / Explain / Verify behavior

The shared depth path is:

```text
Conclusion -> Explain -> Verify -> return to the same conclusion
```

- Explain adds one layer of comparison, composition, time, or causality.
- Verify provides exact values, basis, period, data date, assumptions, sources, contradictory evidence, and material caveats.
- Exact tables remain primary when cross-row/column reconciliation is the job, especially advisor and manager attribution.
- Evidence opens from a claim ID and briefing snapshot, and closing it restores workflow step, scroll/focus, and presentation position.
- Material caveats sit beside the affected claim; secondary methodology stays deeper.
- Evidence never exposes chain of thought or unrelated provenance machinery.

## 13. External manager story translation

- Translate; do not endorse.
- Not verified.
- Not a recommendation.
- Candidate proxies require separate approval and remain internal.
- Advisor/internal is the v1 default unless Frank approves broader exposure.
- Portfolio Through External Lens, Manager by External Lens, Scenario Downside under External Story, and Scenario by Lens remain gated until approved inputs, methods, report shapes, and governance exist.
- The governance caveat cannot be removed by template editing.
- No translated narrative or candidate proxy becomes a production recommendation.

## 14. Plan Check / Objective Horizon treatment

- **The Plan Check** is selected only for the first client-facing “How am I doing?” story.
- **Objective Horizon** is preferred for continued refinement but is not a frozen global visual system or application architecture.
- **Wealth Journey** and **Stewardship Brief** remain non-selected comparison inputs.
- Objective Horizon semantics—direct labels, favorable right/unfavorable left, and portfolio-to-manager context—may be refined where valid.
- Cash bridges, scenario number lines, lens composition, and exact attribution tables remain report-family-specific forms.
- Tables remain primary when exact reconciliation is the task.
- Design-only objectives, tolerances, boundaries, and probability ranges are not client facts or defaults.

## 15. Custom creation scope

### Recommendation for v1

Support built-in use plus **duplicate/edit/save as a reusable custom template**. Defer from-scratch creation as a default ordinary path.

Allowed editable fields:

- name, audience, and purpose;
- included approved sections and order;
- client-facing versus advisor-review visibility within allowed bounds;
- optional-step inclusion;
- plain-language emphasis and exclusions;
- advisor/client caveat wording where not governance-locked.

Locked or constrained fields:

- internal workflow/report IDs and source paths;
- superseded reports;
- gate status without satisfying prerequisites;
- external-story translated/not-verified/not-endorsed/not-recommendation status;
- proxy approval state;
- analytics methodology, renderer settings, and arbitrary schema/data bindings.

The existing from-scratch report-element composer may remain in Developer / QA during migration but is not the recommended ordinary v1 authoring architecture.

## 16. Gating and readiness

Internal gate reasons:

- `missing_data`
- `missing_approved_method`
- `missing_report_shape`
- `missing_benchmark_or_proxy`
- `awaiting_advisor_approval`
- `not_for_audience`

Ordinary UI shows calm language such as “Not ready — an approved benchmark is required,” never raw codes. Advisors see a gated step only when it helps understand workflow completeness. Client Preview/Presentation hide it unless a concise material caveat must qualify an accepted claim. No fake output, empty chart, or readiness report substitutes for the missing client answer.

## 17. Information-budget rules

1. One user job per focused state.
2. One visually dominant action.
3. Show useful output before construction machinery.
4. Use progressive disclosure.
5. Prefer fewer, larger decisions.
6. No raw artifact paths, filenames, workflow IDs, run IDs, JSON, schemas, model/agent language, or implementation status in ordinary UI.
7. Hide technical/admin controls until separately requested.
8. Every visible item must justify its presence for the current job.
9. A client presentation state contains one conclusion and no more than three primary figures unless exact comparison itself is the job.
10. Technical capability does not create a user-facing object or navigation item.

## 18. Implementation acceptance criteria for later UI wiring

`Advisor Workflow UI Wiring v1` must eventually:

- implement the approved first-screen chooser and four business-language Briefing types;
- preserve exact workflow order/status/visibility from committed JSON;
- implement the approved two-object template/briefing lifecycle;
- support built-in use and bounded duplicate/edit/save-as-custom behavior;
- make current-data creation produce a new dated browser-local briefing;
- separate Advisor Review, Client Preview, Presentation, Historical Reading, and Developer / QA;
- enforce the visibility/gating matrix and external-story governance locks;
- hide raw artifact identifiers in ordinary paths;
- preserve contextual Explain/Verify and exact return;
- use exact attribution tables with correct responsibility/denominator semantics;
- keep Plan Check/Objective Horizon scope bounded;
- add focused static/API tests for labels, routes, order, visibility leakage, gate language, immutable history, and external-story caveats;
- pass embedded JavaScript parsing, focused FastAPI/static tests, and local browser rehearsal with synthetic data.

It must not modify analytics, workflow JSON meaning, report mockups, deployment, Docker, live data, or production persistence.

## 19. Open questions / Frank approval gates

Blocking decisions are maintained in `docs/project_control/ARANGUR_UI_BLUEPRINT_FRANK_REVIEW_ITEMS_v1.md`.

UI wiring is blocked on approval of:

1. Conversation Briefing Desk architecture.
2. `Briefing type`, `Briefing template`, and `Briefing` vocabulary.
3. First-screen question and dominant action.
4. Two-object immutable lifecycle and persistence deferral.
5. Duplicate/edit custom scope and from-scratch deferral.
6. Advisor-review/client-preview promotion defaults.
7. External Story advisor/internal default and persistent caveat.
8. Plan Check/Objective Horizon scope and remaining design stage gates.
9. Client objective sourcing and no-objective language.
10. Attribution and gated-step visibility defaults.

## 20. Out of scope

- UI implementation or workflow wiring in this tranche.
- Docker or deployment changes.
- AWS/Lightsail/Cloudflare/DNS work.
- Real holdings, real client data, or live Plaid/custodian integration.
- New scenario, lens, attribution, timing, dollar P&L, or probabilistic math.
- Blended/all-in attribution.
- Position-level drill-down.
- Internal analytics studio/control-plane UI.
- Production benchmark/proxy approval workflow.
- Private-data execution implementation.
- Production pricing/market data.
- Production-grade rendering/export/share engine.
- Durable production persistence unless separately approved.
- Current-versus-proposed portfolio analytics.
- Investment recommendations, trade/order execution, or autonomous actions.

## Approval statement

Frank approved the architecture, vocabulary, lifecycle, custom-creation scope, and visibility defaults for the bounded local implementation tranche on 2026-07-15. The local implementation and acceptance evidence are recorded in `docs/demo/advisor_workflow_ui_wiring_v1.md`; production persistence, deployment, real data, and new analytics remain separately gated.
