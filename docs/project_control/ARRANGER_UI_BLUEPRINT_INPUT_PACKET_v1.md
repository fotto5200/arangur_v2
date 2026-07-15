# Arangur UI Blueprint Input Packet v1

Status: consolidated controller input for `Advisor Workflow UI Integration Blueprint v1`

Prepared: 2026-07-15

Purpose: extract and reconcile existing project-control, repo-canonical workflow/UI, and external design-lab evidence. This packet does not select a new product design and does not authorize UI implementation.

Status vocabulary used below:

- **Accepted**: durable repo direction or implemented product rule.
- **Candidate**: design input that has not been accepted as repo-canonical product direction.
- **Provisional**: active direction with remaining design, data, or lifecycle decisions.
- **Superseded**: retained as history/reference but not the target product surface.
- **Diagnostic**: useful analysis or control material that is not the default client/product surface.
- **Gated**: unavailable until data, method, report shape, or approval prerequisites exist.
- **Needs Frank review**: a product choice that the next blueprint must expose rather than assume.

## 1. Executive Summary for ChatGPT Controller

Arangur v2 is no longer waiting for a basic report catalog or a proof that portfolio evidence can be presented. The repository contains a working synthetic, browser-local private-demo app; four committed audience-specific workflow definitions; accepted report-family classifications; generated report views and product-review mockups; advisor policy and manager mandate attribution separated into distinct responsibility layers; and a local lifecycle in which a briefing template can generate a dated report that can be opened and presented. The analytics and report-design foundation is therefore substantially ahead of the application-level user experience. Sources: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`, `docs/demo/advisor_report_workflows.md`, `docs/product/report_workflow_catalog_v1.md`, and `data/simulation/report_workflows/demo_workflows_v1/report_workflow_catalog_manifest.json`.

The next strategic step is **Advisor Workflow UI Integration Blueprint v1** because two bodies of work now need deliberate reconciliation before more production UI code is changed. The repo has a current operational model built around briefing templates, generated reports, an advisor builder, client/advisor report sets, browser-local storage, and Developer / QA separation. The external Arangur UI Design Lab has a newer design constitution, six user jobs, three competing application architectures, a proposed immutable briefing/template object model, a selected client-report story, a preferred but unfrozen visual direction, and two disposable HTML prototypes. The design lab is high-value input, but it is not repo-canonical and explicitly prohibits silently combining competing architectures or beginning production implementation before approval. Sources: `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`, `C:/Users/fotto/cursor/Arangur UI Design Lab/ARANGUR_UI_DESIGN_LAB_INSTRUCTIONS.md`, and `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_interaction_directions_v1.md`.

The completed project-control tranche established a durable dossier, exhaustive documentation inventory, decision register, UI-design digest, integration queue, and machine-readable inventory. It identified four product surfaces that must remain distinct: the advisor workflow surface, the client reporting surface, the private client-data execution layer, and the Arangur internal analytics control plane. It also confirmed the four accepted workflow families: Principal / Family Office Briefing; Engaged Client / Investment Committee Review; Advisor / Manager Oversight; and External Manager Story Translation. Sources: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`, `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`, and `docs/project_control/arranger_project_control_inventory_v1.json`.

The blueprint should not revisit accepted analytics architecture. Full portfolio revaluation controls scenario impact; lenses classify after valuation rather than price positions; advisor policy attribution and manager mandate attribution remain separate; equal-weight AI attribution is diagnostic unless explicitly adopted as policy; Advisor Policy Attribution v2 supersedes the Policy-Level Attribution Summary v1 as the primary product surface; external manager stories are translated rather than endorsed; candidate proxies require approval; and readiness artifacts are not substitutes for client answers. Sources: `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` and `docs/product/report_family_acceptance_status_v1.md`.

The principal reconciliation work is product and interaction architecture. The blueprint must decide what the first screen asks, whether the ordinary user begins from a business job, a recent briefing, or a durable object library, and whether the application architecture is Briefing Desk, Arangur Guide, Investment Library, or an explicitly approved alternative. It must define a canonical object lifecycle and vocabulary across `workflow`, `template`, `briefing`, `report set`, and `generated report`; define the amount of custom template/workflow creation in v1; separate builder, advisor review, client preview, presentation, and historical reading; define how immutable dated outputs relate to reusable templates; and specify how accepted, advisor-only, setup/readiness, internal-control, diagnostic, optional, and gated steps appear. Sources: `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`, `docs/ui_reporting/briefing_set_builder_model_v1.md`, `docs/demo/advisor_report_workflows.md`, and `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_user_jobs_v1.md`.

At the client-report level, The Plan Check is selected only as the storytelling direction for the first client-facing “How am I doing?” report. Objective Horizon is preferred for continued refinement, but it is neither a global visual system nor an application architecture. Wealth Journey and Stewardship Brief remain non-selected comparison inputs. Tables should remain primary when exact cross-row reconciliation is the task—especially attribution—while most reports should lead with a conclusion and reveal explanation and evidence progressively. Design-only values such as the 6.5% return objective, 4.0% growth objective, ±3 percentage-point tolerance, -15% downside boundary, and illustrative probability range are not client facts. Sources: `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_selected_direction_v1.md`, `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_objective_horizon_manager_refinement_v1.md`, and `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_report_breadth_test_v1.md`.

The most important unresolved decisions are therefore: application architecture; canonical vocabulary and object lifecycle; first-screen question; custom creation scope; the default separation between advisor review and client preview; whether External Manager Story Translation is advisor/internal only in v1; how material caveats and gated steps appear; whether immutable historical briefings become durable backend objects now or later; and which design-lab stage gates must precede UI wiring. These require Frank’s review. The blueprint should make them explicit and testable, not invent answers. Source: `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md` and `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`.

## 2. Source Files Read

| File path | File type | Read status | Why it matters | Key topics extracted |
| --- | --- | --- | --- | --- |
| `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md` | Markdown | Fully read | Primary project-state handoff | Four product surfaces, four workflows, accepted reports, UI state, source-of-truth rules, next phase |
| `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md` | Markdown | Fully read | Reconciles repo UI evidence with external design work | Requirements, alternative architectures, report-story selection, prototype digest, Frank-review items |
| `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md` | Markdown | Fully read | Defines the immediate tranche and boundaries | Blueprint inputs, required decisions, later wiring scope, do-not-build list |
| `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` | Markdown | Fully read | Durable accepted/provisional/superseded decision map | Analytics rules, workflow/UI principles, unresolved architecture, gated behavior |
| `docs/project_control/ARRANGER_DOCUMENTATION_INVENTORY_v1.md` | Markdown | Fully read | Exhaustive map of repo and design-lab evidence | Source freshness, read coverage, relevant UI docs, mockups, workflow artifacts, prototypes |
| `docs/project_control/arranger_project_control_inventory_v1.json` | JSON | Fully read | Machine-readable discovery checkpoint | Counts, high-relevance files, key decisions, warnings, next tranche |
| `docs/product/report_workflow_catalog_v1.md` | Markdown | Fully read | Repo-canonical definition of workflows versus report families | Four audience conversations, setup notes, accepted attribution order |
| `docs/product/report_family_acceptance_status_v1.md` | Markdown | Fully read | Canonical report status sheet | Primary/supporting/advisor-only/setup/diagnostic/superseded classifications |
| `docs/ui_reporting/ui_reporting_philosophy_v1.md` | Markdown | Fully read | Foundational repo UI philosophy | Client-question-first, briefing-room metaphor, advisor/client separation, hidden workflow machinery |
| `docs/ui_reporting/briefing_set_builder_model_v1.md` | Markdown | Fully read | Most complete repo builder model | Shared context, ordered report views, preview, saved set, build/preview/adjust/save loop |
| `docs/ui_reporting/briefing_set_client_preview_model_v1.md` | Markdown | Fully read | Defines client preview behavior | Ordered rendering, plain English, compact caveats, advisor-only exclusions, artifact suppression |
| `docs/ui_reporting/guided_briefing_builder_correction_v1.md` | Markdown | Fully read | Records the simplified UI correction and later evolution | One choice at a time, dense-console rejection, one-report wizard supersession |
| `docs/demo/advisor_report_workflows.md` | Markdown | Fully read | Documents current implemented private-demo lifecycle | Template → current-data generation → generated report → open/present; built-ins and browser-local history |
| `data/simulation/report_workflows/demo_workflows_v1/report_workflow_catalog_manifest.json` | JSON | Fully read | Canonical workflow manifest | Four workflows, synthetic/non-production limits, not yet canonical UI wiring |
| `data/simulation/report_workflows/demo_workflows_v1/principal_family_office_briefing_minimal_v1.json` | JSON | Fully read | Exact minimal client workflow | Seven ordered steps, visibility, one gated advisor-plan handoff |
| `data/simulation/report_workflows/demo_workflows_v1/engaged_client_investment_committee_review_v1.json` | JSON | Fully read | Exact sophisticated-client workflow | Nine ordered steps, advisor-review depth, optional dense matrix |
| `data/simulation/report_workflows/demo_workflows_v1/advisor_manager_oversight_v1.json` | JSON | Fully read | Exact advisor-only oversight workflow | Nine ordered steps, diagnostics, internal handoff, gated manager coverage |
| `data/simulation/report_workflows/demo_workflows_v1/external_manager_story_translation_v1.json` | JSON | Fully read | Exact translation workflow | Setup notes, internal candidate proxies, four gated reports, governance close |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/ARANGUR_UI_DESIGN_LAB_INSTRUCTIONS.md` | Markdown | Fully read | Design constitution and stage gates | One job/action, progressive disclosure, three directions, prototype before production, no silent invention |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_user_jobs_v1.md` | Markdown | Fully read | Proposed interaction-level object model and six jobs | Briefing/template/alignment/evidence vocabulary, immutability, presentation, generation, authoring, history |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_interaction_directions_v1.md` | Markdown | Fully read | Defines the unresolved application architectures | Briefing Desk, Arangur Guide, Investment Library, state contracts and failure modes |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` | Markdown | Fully read | Client-report communication contract | Plan Check, Wealth Journey, Stewardship Brief, depth model, caveats, prototype scripts |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_selected_direction_v1.md` | Markdown | Fully read | Records the limited report-story selection | Plan Check selected only for first client report; Objective Horizon next refinement |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_plan_check_visual_concepts_v1.md` | Markdown | Fully read | Compares three visual concepts within Plan Check | Objective Horizon, Capital Landscape, Editorial Focus, selection boundary |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_objective_horizon_manager_refinement_v1.md` | Markdown | Fully read | Refines portfolio-to-manager presentation | Stable semantic direction, responsibility language, contextual drill-down, breadth gate |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_report_breadth_test_v1.md` | Markdown | Fully read | Tests shared reporting language across report families | Cash bridge, scenario number line, lens composition, exact advisor/manager tables |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_objective_horizon_manager_refinement_v1.html` | HTML prototype | Partially read; source-inspected | Disposable interaction specimen | Three steps, Managers A–F, Explain/Verify, Previous/Next, contextual return |
| `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_report_breadth_test_v1.html` | HTML prototype | Partially read; source-inspected | Cross-report visual-language specimen | Five report selectors, opening/explain states, scenario/lens visuals, attribution tables |

## 3. Four Product Surfaces

### Advisor workflow surface

| Field | Current understanding |
| --- | --- |
| Purpose | Help an advisor choose a business conversation, reuse or compose an ordered template/workflow, generate with a dated data snapshot, review the output, and present it. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| Users | Advisors, relationship managers, CIOs, investment teams, and client-service staff. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| What exists now | Dependency-free browser app; four built-in catalog definitions adapted into briefing templates; browser-created templates; ordered client/advisor sets; builder; current-data generation; preview/presentation; browser-local generated-report shelf; Developer / QA separation. Source: `docs/demo/advisor_report_workflows.md`. |
| What is not built yet | An approved application architecture; final canonical vocabulary; durable persistence/history; production workflow persistence; fully reconciled workflow-catalog chooser and design-lab contract. Sources: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md` and `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`. |
| UI implications | Entry should be job/conversation-led and business-language-first; builder power must be separated from presentation simplicity; ordered steps must preserve visibility/gate metadata; raw IDs and artifacts stay out of the ordinary path. Sources: `docs/product/report_workflow_catalog_v1.md` and `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`. |
| Risks/open questions | Briefing Desk vs Guide vs Library; “workflow” as internal or visible term; custom creation scope; template versus generated-briefing lifecycle; historical object durability; over-configuration. Source: `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`. |

### Client reporting surface

| Field | Current understanding |
| --- | --- |
| Purpose | Present an advisor-approved, dated narrative with the conclusion first, evidence on demand, and technical machinery hidden. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| Users | Principals, family-office members, sophisticated clients, investment committees, and advisor presenters. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| What exists now | Client/advisor preview models, generated HTML/Markdown report fragments, accepted mockups, browser presentation with Previous/Next, and two disposable visual prototypes. Sources: `docs/demo/advisor_report_workflows.md` and `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`. |
| What is not built yet | Final client presentation system, production-grade rendering/share/export, durable immutable historical library, validated client objective/threshold data, and production/client-ready data. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| UI implications | Preserve the advisor-selected order; use Understand → Explain → Verify → exact return; one conclusion and action per state; material caveats adjacent to claims; no generation/edit/admin controls; exact tables only when comparison/reconciliation is the job. Sources: `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` and `docs/ui_reporting/briefing_set_client_preview_model_v1.md`. |
| Risks/open questions | Unsupported “on plan” claims; illustrative values mistaken for client facts; deterministic versus probabilistic semantics; client access to attribution depth; Objective Horizon applied too broadly. Sources: `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_selected_direction_v1.md` and `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`. |

### Private client-data execution layer

| Field | Current understanding |
| --- | --- |
| Purpose | Ingest and process client holdings while minimizing unnecessary Arangur visibility into private information. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| Users | Advisory firms, authorized operations/administration, data custodians; advisors and clients consume governed outputs rather than construction controls. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| What exists now | Source-neutral portfolio contracts, Plaid-shaped mock ingestion, synthetic fixtures, optional Postgres skeletons, local Docker/private-demo packaging, and explicit no-real-data boundaries. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| What is not built yet | Production custodian/Plaid adapters, tenant isolation, entitlements, encryption/key management, audit/retention, formal minimization topology, and approved hosted-versus-client-controlled execution. Source: `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-14). |
| UI implications | The advisor blueprint may define readiness/error contracts but must not design private-data administration into the ordinary advisor/client path. Source: `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`. |
| Risks/open questions | Real identifiers leaking through artifacts/logs; local persistence mistaken for production privacy; UI assumptions hardening before locality, tenancy, and consent are defined. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |

### Arangur internal analytics control plane

| Field | Current understanding |
| --- | --- |
| Purpose | Curate, validate, approve, version, and publish analytic packs containing lenses, scenarios, shocks, coverage/confidence rules, valuation support, and report capabilities. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| Users | Internal analytics, investment/research, model governance, and QA teams—not ordinary advisors or clients. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| What exists now | Publish/consume boundary, analytic-pack contract, synthetic pack, scenario/lens/valuation designs, calculated attribution engines, and proof outputs. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |
| What is not built yet | Internal studio UI, live data, production pricing coverage, approval/version workflows, operational publishing, and production governance. Source: `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-13). |
| UI implications | Advisor UI consumes approved packs and may show governed readiness/caveats; it must not expose analytic construction, proxy approval, or model-governance controls. Sources: `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md` and `docs/product/report_workflow_catalog_v1.md`. |
| Risks/open questions | Synthetic packs treated as recommendations; unapproved proxies/methods shown to clients; studio work consuming the next UI tranche; control-plane concerns mixed into advisor navigation. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`. |

## 4. Accepted Workflow Families

### Principal / Family Office Briefing

- **Audience:** principal or family-office member; minimal client depth.
- **Core user question:** “What do I need to know without reading every analytic report?”
- **Conversation goal:** establish where the portfolio stands, what cash it delivered, whether spending is supported, broad ownership, major downside, and the advisor’s future plan.
- **Ordered flow:** Portfolio Representation Status → Cash Flow Delivered → Cash-Flow Support Outlook → Coverage and Confidence Warning → Aggregated Asset Allocation → Current Portfolio Scenario Downside → High-Level Advisor Plan / Next-Year Positioning.
- **Client/advisor status:** client-facing minimal; Coverage and Confidence Warning is advisor-review support; the advisor-plan handoff is client-facing but gated because no approved/generated shape exists.
- **Future UI:** business-language template/workflow choice, ordered client journey, compact material readiness warning, calm gated final handoff, and optional evidence.
- **Hide/gate:** raw coverage mechanics, dense attribution, artifact paths, and any invented positioning/recommendation.
- **Sources:** `data/simulation/report_workflows/demo_workflows_v1/principal_family_office_briefing_minimal_v1.json` and `docs/product/report_workflow_catalog_v1.md`.

### Engaged Client / Investment Committee Review

- **Audience:** engaged client, sophisticated principal, or family investment committee.
- **Core user question:** “How did policy, managers, exposures, themes, and scenarios explain the portfolio?”
- **Conversation goal:** combine allocation, responsibility, thematic exposure, and downside evidence without turning the meeting into internal diligence.
- **Ordered flow:** Portfolio Representation Status → Policy Allocation Review → Advisor Policy Attribution by Manager/Sleeve → Manager Mandate Attribution Summary → Full Lens Exposure—AI Adoption → Full Lens Exposure—Energy Security → Manager by Lens Exposure—AI Adoption → Current Portfolio Scenario Downside → optional Manager Driver Attribution Matrix.
- **Client/advisor status:** sophisticated-client workflow; policy/manager attribution and manager-by-lens steps are advisor-review by default; the dense matrix is optional advisor/committee support.
- **Future UI:** client-facing journey with deliberate advisor-review/preview decisions, lens explanations, scenario close, and optional exact attribution depth.
- **Hide/gate:** internal diligence by default, technical denominators until needed, and the dense matrix in a five-minute opening.
- **Sources:** `data/simulation/report_workflows/demo_workflows_v1/engaged_client_investment_committee_review_v1.json` and `docs/product/report_workflow_catalog_v1.md`.

### Advisor / Manager Oversight

- **Audience:** advisor and internal investment team.
- **Core user question:** “Which mandates, managers, implementation effects, and review flags need attention before client conversations?”
- **Conversation goal:** monitor allocation drift, benchmark basis, advisor policy decisions, manager implementation, driver details, reconciliation, and evidence quality.
- **Ordered flow:** Policy Allocation Drift Summary → Manager Mandate Benchmark Basis → Advisor Policy Attribution → Manager Mandate Attribution Summary → Manager Driver Attribution Matrix → Within-Manager Attribution Detail → Manager Implementation Handoff → Coverage and Confidence Warning → Coverage/Confidence by Manager.
- **Client/advisor status:** advisor-only diagnostic workflow; some middle steps are advisor-review, the handoff is internal control, and manager-sliced coverage is gated.
- **Future UI:** exception-first overview, priority manager path, exact tables where reconciliation is the job, contextual manager drill-down, exact return to the portfolio/oversight state.
- **Hide/gate:** fully aligned managers, internal handoff from clients, raw scoring mechanics, and manager-sliced coverage until its report/data shape exists.
- **Sources:** `data/simulation/report_workflows/demo_workflows_v1/advisor_manager_oversight_v1.json` and `docs/product/report_workflow_catalog_v1.md`.

### External Manager Story Translation

- **Audience:** advisor, investment committee, or manager-facing discussion.
- **Core user question:** “How would Arangur translate an outside manager worldview into lenses, scenarios, proxies, and report workflows?”
- **Conversation goal:** structure an external narrative without treating it as true, verified, endorsed, or recommended.
- **Ordered flow:** Manager Story Summary → Implied Lenses → Key-Price Scenario Set → Candidate Benchmark/Proxy Map → Portfolio Through External Lens → Manager by External Lens → Scenario Downside under External Story → Scenario by Lens → Governance/Caveat Note.
- **Client/advisor status:** not client-facing until reviewed; the first three and final note are advisor-review setup artifacts, candidate proxies are internal control, and the four analytic report steps are gated.
- **Future UI:** persistent translated/not-endorsed status, candidate/approval labels, visible prerequisites, and a governance close. First-release exposure should remain advisor/internal unless Frank decides otherwise.
- **Hide/gate:** candidate proxy details from clients; all four portfolio/manager/scenario report promises until data, method, report shapes, and approvals exist.
- **Sources:** `data/simulation/report_workflows/demo_workflows_v1/external_manager_story_translation_v1.json`, `docs/product/external_manager_story_workflow_v1.md`, and `data/simulation/external_story_translation/external_manager_story_translation_pack_v1/`.

## 5. Accepted Report and Attribution Architecture

### Report-family architecture

| Family | Accepted current role | Important UI treatment | Sources |
| --- | --- | --- | --- |
| Portfolio, cash-flow, and status | Portfolio Representation Status, Cash Flow Delivered, Cash-Flow Support Outlook, and Aggregated Asset Allocation are accepted primary; Allocation by Manager and consistent-category concentration are supporting; Coverage and Confidence Warning is advisor/setup unless material. | Establish business context; separate trailing cash delivered from forward support; readiness must not replace the answer. | `docs/product/report_family_acceptance_status_v1.md`; `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md` |
| Scenario, lens, and exposure | Current Portfolio Scenario Downside and Full Lens Exposure for AI Adoption/Energy Security are accepted primary; Manager by Lens is supporting; scenario-by-lens and unapproved ranges remain gated. | Use full-revaluation results; keep common bases/scales/horizons; distinguish deterministic points, sensitivity ranges, and probability ranges. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`; `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_report_breadth_test_v1.md` |
| Policy allocation | Policy Allocation Review is accepted primary; Policy Allocation Drift Summary is advisor-only; Imputed Current Allocation Baseline and Manager Mandate Benchmark Basis are setup/readiness. | Client surface shows policy alignment; advisor surface shows drift and benchmark readiness. | `docs/product/report_family_acceptance_status_v1.md` |
| Advisor policy attribution | Advisor Policy Attribution by Manager/Sleeve is accepted primary; Advisor Policy Effect Totals is supporting. | Keep a portfolio-effect denominator and show advisor-controlled decisions before manager implementation. | `docs/product/report_family_acceptance_status_v1.md`; `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-05, D-07) |
| Manager mandate attribution | Manager Mandate Attribution Summary is accepted primary; Manager Driver Attribution Matrix is accepted supporting; Within-Manager Detail is advisor-only; Implementation Handoff is diagnostic/control. | Keep manager responsibility and assigned-mandate basis separate from advisor allocation decisions; use exact tables for reconciliation. | `docs/product/report_family_acceptance_status_v1.md`; `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-05, D-08) |
| External manager story translation | Story summary, implied lenses, key-price scenarios, candidate proxies, gated report map, and governance caveats form the accepted translation pack. | Always state translated/not verified/not endorsed/not a recommendation; candidate proxies remain approval-required. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-09, D-10); `data/simulation/external_story_translation/external_manager_story_translation_pack_v1/` |

### Accepted attribution split

**Advisor policy attribution** evaluates decisions made before manager implementation:

1. **Selected mandate effect** — the neutral selected-mandate basket versus the global benchmark.
2. **Target weighting effect** — target policy weights versus neutral selected-mandate weights.
3. **Funding drift effect** — actual funding weights versus target weights.
4. **Advisor policy effect** — the additive total before manager implementation.

**Manager attribution** evaluates implementation within assigned capital and mandate:

1. **Actual capital** — the capital and/or weight assigned to the manager, reported on the explicitly named basis.
2. **Manager mandate benchmark** — the approved benchmark defining the manager’s assigned job.
3. **Active return versus mandate** — manager return less its mandate benchmark, kept separate from weight-adjusted portfolio contribution.
4. **Manager Driver Attribution Matrix** — manager/selected-manager decisions decomposed into mandate sub-benchmark selection, mandate sub-benchmark sizing, asset/security selection, asset/security sizing, and residual/unexplained, with totals reconciled on the declared denominator.

This split must not be blended because advisor allocation choices and manager implementation choices have different responsibility, capital, and denominators. Sources: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`, `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-05), and `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_report_breadth_test_v1.md`.

### Superseded and diagnostic items

| Item | Status | Required treatment | Source |
| --- | --- | --- | --- |
| Policy-Level Attribution Summary v1 | Superseded as primary surface | Retain as calculation/reference evidence; do not restore as default product review. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-07) |
| Equal-weight AI attribution | Diagnostic unless equal weight is explicitly selected policy | State the diagnostic basis; do not call it the client’s policy. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-06) |
| Cash-Flow Support Readiness as client report | Superseded | Use Cash Flow Delivered and Cash-Flow Support Outlook when prerequisites exist; readiness remains advisor/setup. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` |
| Old dense console | Superseded as main advisor UI | Preserve technical evidence in Developer / QA or admin layers only. | `docs/ui_reporting/guided_briefing_builder_correction_v1.md` |
| One-report guided wizard | Superseded as target model | Retain its sparse/progressive discipline; target an ordered briefing/workflow set. | `docs/ui_reporting/briefing_set_builder_model_v1.md` |
| Mixed-category concentration table | Superseded | Use one consistent category system per report. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` |

## 6. UI Requirements Extracted from Design Lab and Project-Control Docs

| Requirement | Why it matters | Source file/path | Status | UI blueprint implication |
| --- | --- | --- | --- | --- |
| Workflow/job-first advisor entry | Starts from the conversation instead of report inventory or technical execution. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-11); `docs/ui_reporting/ui_reporting_philosophy_v1.md` | Accepted; visible word needs Frank review | Define a business-language chooser for the four canonical families and decide whether `workflow` remains internal. |
| One user job and one dominant action per state | Reduces decision overload and makes state intent legible. | `C:/Users/fotto/cursor/Arangur UI Design Lab/ARANGUR_UI_DESIGN_LAB_INSTRUCTIONS.md` | Accepted design principle | Every screen/state contract must name its job, minimum outcome, and dominant action. |
| Progressive disclosure | Keeps technical depth available without making it the product surface. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-15); `C:/Users/fotto/cursor/Arangur UI Design Lab/ARANGUR_UI_DESIGN_LAB_INSTRUCTIONS.md` | Accepted | Specify initial, Explain, Verify, admin, and Developer / QA depths. |
| Conclusion-first reporting | Lets clients understand consequence before methodology. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` | Accepted reporting principle | Each presentation state begins with one plain-English conclusion and material caveat. |
| Advisor builder versus client presenter | Composition and presentation are different jobs with different density. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-12); `docs/ui_reporting/briefing_set_builder_model_v1.md` | Accepted | Define distinct Builder, Advisor Review, Client Preview, Presentation, and Historical Reading states. |
| Advisor review versus client preview | The same underlying evidence requires different visibility and language. | `docs/ui_reporting/briefing_set_client_preview_model_v1.md`; `data/simulation/report_workflows/demo_workflows_v1/` `audience_visibility` values | Accepted; defaults need Frank review | Produce a visibility matrix for client-facing, advisor-review, advisor-only, setup, internal-control, and gated steps. |
| Workflow/reusable templates | Repeated meetings need reusable intent and ordered content without regenerating setup manually. | `docs/demo/advisor_report_workflows.md`; `docs/ui_reporting/briefing_set_builder_model_v1.md` | Accepted capability; vocabulary unresolved | Preserve built-in and custom reuse while defining the canonical user-facing object and lifecycle. |
| Custom workflow creation | Advisors need purposeful composition, but a universal report generator would recreate console complexity. | `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`; `docs/ui_reporting/briefing_set_builder_model_v1.md` | Needs Frank review | Choose whether v1 allows editing approved templates, saving new templates, or both; constrain fields to audience, purpose, order, emphasis, exclusions, visibility, and gates. |
| Ordered report journey view | A meeting is a sequence, not a collection of peer analytics. | `docs/product/report_workflow_catalog_v1.md`; `docs/ui_reporting/briefing_set_builder_model_v1.md` | Accepted | Use compact agenda/outline/guided steps based on the selected architecture; preserve canonical order and optionality. |
| Immutable dated briefings versus reusable templates | Historical trust requires fixed claims and dates; reusable definitions must not look like generated documents. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-16); `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_user_jobs_v1.md` | Provisional / needs Frank review | Define template lineage, generated/date/data-date identity, “use current data creates new,” and whether durable persistence is now or later. |
| Gated/deferred report visibility | Missing prerequisites must not become fabricated reports or misleading client-readiness cards. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-20); `data/simulation/report_workflows/demo_workflows_v1/` | Accepted | Define calm unavailable states and reason categories: missing data, approved method, proxy/benchmark, report shape, or advisor approval. |
| External-story caveats | Translation can otherwise be mistaken for endorsement or recommendation. | `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` (D-09, D-10); `data/simulation/report_workflows/demo_workflows_v1/external_manager_story_translation_v1.json` | Accepted | Persist caveat status through chooser, review, evidence, and any eventual client preview; keep candidate proxies internal. |
| Artifact-name suppression | Paths, IDs, filenames, and runs expose implementation rather than business meaning. | `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`; `docs/ui_reporting/briefing_set_client_preview_model_v1.md` | Accepted | Use business titles/questions/readiness; place IDs/paths/run data in evidence or Developer / QA only. |
| Plain-English labels | Advisors and clients should not need to translate schema or platform concepts. | `C:/Users/fotto/cursor/Arangur UI Design Lab/ARANGUR_UI_DESIGN_LAB_INSTRUCTIONS.md`; `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_user_jobs_v1.md` | Accepted | Ban prompt/model/agent/run/schema/JSON terminology from ordinary states; define approved business labels in the blueprint. |
| Minimal UI clutter | Capability is not sufficient reason for a panel or control. | `C:/Users/fotto/cursor/Arangur UI Design Lab/ARANGUR_UI_DESIGN_LAB_INSTRUCTIONS.md`; `docs/ui_reporting/guided_briefing_builder_correction_v1.md` | Accepted | Add an information budget and specify what is hidden in each state. |
| Exact tables only where reconciliation is the task | Tables are essential for auditability in attribution but harmful as default narrative openings. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_report_breadth_test_v1.md`; `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` | Accepted | Keep tables primary for advisor/manager attribution; use them at Verify depth elsewhere. |
| Evidence in context with exact return | Trust depends on verifying one claim without losing the conversation. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_user_jobs_v1.md`; `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` | Accepted | Define claim-bound evidence routes and exact back-navigation/state restoration. |
| Stable scenario bases, scales, and horizons | Visual comparisons become misleading when axes or definitions change. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_selected_direction_v1.md`; `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_report_breadth_test_v1.md` | Accepted | Blueprint must require explicit base/unit/horizon and preserve them across compared scenarios. |
| Material caveats adjacent to claims | Caveats should change interpretation without becoming a competing disclaimer block. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` | Accepted | Define materiality and placement; move secondary methodology deeper. |
| Client objectives before benchmark comparison | Positive performance or benchmark outperformance does not prove that a client is on plan. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` | Accepted principle; objective sourcing unresolved | Allow precise outcome language when objectives are absent; prohibit invented plan-status conclusions. |

## 7. Alternative UI Approaches and Design Directions

| Name | Concept / problem solved | Strengths | Weaknesses | Current status | Carry forward | Reject or defer | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Plan Check | Organizes the first client “How am I doing?” report around relevant Return, Capital Growth, Cash Support, and Resilience objectives. | Direct plan-status answer; repeatable review structure; exceptions stay visible. | Can become a scorecard; requires real objectives and boundaries. | **Selected only for the first client-report story; provisional.** | Objective-first narrative, no more than 2–3 opening objectives, Understand → Explain → Verify. | Do not infer an application architecture or global UI style. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_selected_direction_v1.md`; `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` |
| Objective Horizon | Uses directly labeled objective/boundary measures with favorable-right and unfavorable-left semantics; extends from portfolio to manager context. | Fast status scan, direct labels, clear responsibility, contextual manager drill-down. | Can become KPI rails; normalization can imply false comparability; breaks with too many objectives. | **Preferred for refinement; not frozen.** | Semantic direction, direct actual/objective labels, portfolio → manager contribution → selected manager → return. | Do not force horizon bars onto cash bridges, scenarios, composition, or attribution tables. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_objective_horizon_manager_refinement_v1.md` |
| The Briefing Desk | Makes the finished dated briefing the center of gravity. | Strong reading/presentation flow, history, evidence anchoring. | Alignment and portfolio switching may feel secondary; document may become a dumping ground. | **Candidate; needs Frank review.** | Distinct reader/presentation states, fixed dates, evidence from claims. | Do not adopt or hybridize before comparison/selection. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_interaction_directions_v1.md` |
| The Arangur Guide | Starts with a business-language request and asks only consequential questions. | Fast for outcome-oriented users; hides system structure; handles ambiguity. | Interpretation risk, conversation clutter, discoverability and stable-artifact concerns. | **Candidate; needs Frank review.** | Business-language entry, concise clarification, answer-first alignment. | Do not assume generative conversation is trusted or sufficient for template maintenance. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_interaction_directions_v1.md` |
| The Investment Library | Organizes durable Briefings, Templates, and Portfolios into focused lifecycles. | Strong retrieval/history, explicit object distinctions and ownership. | Can become a filing system/dashboard; metadata and cross-object navigation can dominate. | **Candidate; needs Frank review.** | Concrete lifecycle distinctions, immutable history, portfolio home for alignment. | Do not expose every backend object or grow a mixed dashboard. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_interaction_directions_v1.md` |
| The Wealth Journey | Explains opening value, flows, ending value, and forward paths through time. | Strong capital/cash reconciliation and meaningful motion. | Requires reliable history; can imply forecast precision and bury objective status. | **Non-selected comparison input.** | Capital-flow distinctions and historical/future visual separation. | Defer as the organizing story unless Frank reopens selection. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` |
| The Stewardship Brief | Organizes outcome, advisor decisions, manager implementation, and forward action around accountability. | Strong governance and sophisticated-client story. | Can feel self-serving, technical, or blame-oriented. | **Non-selected comparison input.** | Responsibility separation and causal explanation at deeper levels. | Defer as the first client-report organizing story. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md` |
| Capital Landscape | Uses a continuous capital path for opening value, change, current value, and forward risk. | Best capital reconciliation and useful animation. | False precision; may drift back into Wealth Journey. | Candidate/reference visual concept. | Capital bridge/path where the report job requires it. | Do not merge into Objective Horizon opening before selection. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_plan_check_visual_concepts_v1.md` |
| Editorial Focus | Uses one declarative sentence and one hero relationship per presentation state. | Calmest five-minute presentation and immediate comprehension. | More steps; may feel oversimplified to sophisticated clients. | Candidate/reference visual concept. | One conclusion and action; strong presentation editing. | Do not make it the global layout without breadth tests. | `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_plan_check_visual_concepts_v1.md` |
| Old dense console | Exposes setup, artifacts, evidence, caveats, run history, and technical detail together. | Useful proof/admin/QA capability. | Overloads the advisor and makes system structure the product. | **Superseded as main UI.** | Preserve capabilities in Developer / QA or protected admin/evidence. | Reject as advisor/client entry architecture. | `docs/ui_reporting/guided_briefing_builder_correction_v1.md` |
| One-report wizard | Guides one question/audience/context into one report. | Sparse pacing and progressive disclosure. | Too small for a real multi-report meeting. | **Superseded as target model.** | One choice at a time and compact prior-choice summaries. | Replace with ordered briefing/workflow composition. | `docs/ui_reporting/briefing_set_builder_model_v1.md` |

## 8. HTML Prototype Digest

### `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_objective_horizon_manager_refinement_v1.html`

| Field | Digest |
| --- | --- |
| Title | **Arangur Objective Horizon Manager Refinement** |
| Apparent prototype | Self-contained static interactive presentation inside a sandboxed `iframe`/`srcdoc`; disposable design evidence, not production code. |
| Major visible sections | Portfolio Horizon; Manager contribution horizon; Selected manager horizon; Managers A–F selector; Explain responsibility; Verify manager evidence; Previous/Next; “1 of 3” progress. |
| Workflow/use case | A Plan Check client presentation that moves from overall portfolio status to manager contributions and one selected manager without forcing separate reports for every manager. |
| UI ideas worth preserving | One conclusion/action per state; favorable-right/unfavorable-left semantics; contextual manager drill-down; explicit advisor-versus-manager responsibility; return to portfolio. |
| Risks/caveats | Uses design-only objectives/tolerances; does not decide application navigation, object lifecycle, production accessibility, data binding, or global visual style. |
| Implementation relevance | Strong input to the client presentation/evidence contract after application architecture and vocabulary are approved; not a production implementation template. |

### `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_report_breadth_test_v1.html`

| Field | Digest |
| --- | --- |
| Title | **Arangur Report Breadth Test v1** |
| Apparent prototype | Self-contained static interactive cross-report design experiment, not a generated report or end-to-end workflow. |
| Major visible sections | Selectors for Cash Support, Scenario Risk, AI Lens, Advisor Attribution, and Manager Attribution; an opening and explain state for each; Previous/Next and progress; exact tables for attribution. |
| Workflow/use case | Tests which visual-language rules transfer across materially different report jobs. |
| UI ideas worth preserving | Conclusion-first openings; cash objective comparison then bridge; scenario points/ranges with stable semantics; part-to-whole lens composition; separate advisor and manager denominators; exact tables when reconciliation is the task. |
| Risks/caveats | The within-manager fixture and probability range are illustrative; the prototype does not freeze a global system; it is not one of the four canonical end-to-end workflows. |
| Implementation relevance | Use as a blueprint test suite for report-family behavior, not as a page to port wholesale. |

Source-inspection notes: titles, state labels, report selectors, controls, and embedded content were inspected; raw HTML is intentionally not reproduced. Sources: the two HTML paths above and `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`.

## 9. Vocabulary and Architecture Conflicts

| Terms involved | Where the conflict appears | Why it matters | Suggested resolution for the blueprint | Needs Frank review? |
| --- | --- | --- | --- | --- |
| `workflow` vs business conversation/briefing type | Repo workflow catalog and current app use workflows; UI philosophy/design lab says implementation terminology should be hidden. | The first-screen label determines whether users see a meeting job or a system object. | Keep `workflow` as the canonical internal/catalog term; choose a business-facing label such as briefing type or conversation only after architecture review. | Yes |
| `briefing template` vs `workflow template` | Current app adapts workflow JSON into briefing templates; design lab defines reusable briefing templates. | Duplicate names can imply duplicate objects or incompatible lifecycles. | Blueprint should define one reusable object mapped to the canonical workflow definition and record aliases only for migration. | Yes |
| `briefing` vs `generated report` | Design lab treats a briefing as dated/immutable and report as a synonym; current app exposes Generated Reports. | History, regeneration, presentation, and client language depend on this identity. | Choose one canonical user-facing generated object; preserve `generated report` as implementation/legacy terminology only if necessary. | Yes |
| `report set` / `briefing set` vs briefing/template | Older repo builder model uses briefing set as a working and future saved presentation set. | It is unclear whether a set is a draft template, a generated document, or a third object. | Avoid a third user-facing object unless its lifecycle is distinct; map ordered report views into either the template definition or generated briefing. | Yes |
| `report view` / report element / report family | Repo composer and contracts use report elements/views/families; design lab uses sections and evidence. | Exposing taxonomy recreates a combinatorial report builder. | Maintain report family/view IDs internally; present client-readable sections/questions and only the few meaningful editing controls. | No for internal mapping; yes for user label |
| `advisor review` vs `client preview` | Workflow JSON has `advisor_review`; repo builder has client/advisor sets; current app and lab have preview/presentation concepts. | Preview can mean rehearsal, approval, or a lower-density rendering. | Define Advisor Review as content/visibility approval; Client Preview as exact rehearsal of client-visible sequence; Presentation as chrome-free delivery. | Yes |
| `client preview` vs `presentation` | Repo preview model and current presentation view overlap. | Controls, dates, and evidence behavior may drift if they are treated as the same state. | Treat preview as advisor-entered rehearsal and presentation as audience-facing mode unless Frank chooses a simpler combined state. | Yes |
| `builder` vs `presenter`/reader | Repo builder allows composition; design lab separates reading, presentation, and template authoring. | One object page can accumulate conflicting actions. | Blueprint must define separate focused states and transition rules, even if they share a shell. | No; separation is accepted |
| `library` vs `guide` vs `desk` | Three design-lab application architectures. | Each selects a different center of gravity: object, objective/conversation, or document. | Compare against all six user jobs and choose one; do not create an implicit hybrid. | Yes |
| `alignment review` vs Advisor / Manager Oversight | Design lab proposes alignment review; canonical workflow is Advisor / Manager Oversight. | They overlap but may differ in breadth, saved-object status, and client relevance. | Treat alignment review as a candidate business-language view/job mapped to the oversight workflow until the blueprint defines its exact scope. | Yes |
| `use current data`, `populate`, `generate`, `regenerate` | Current app has population/generation actions; design lab says current data creates a new immutable briefing. | Historical integrity and user expectations depend on whether data refresh mutates or creates. | Canonicalize a single user action that always creates a new dated object; keep operational verbs internal. | Yes |

Sources: `docs/demo/advisor_report_workflows.md`, `docs/ui_reporting/briefing_set_builder_model_v1.md`, `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`, and `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_user_jobs_v1.md`.

## 10. Source-of-Truth and Project-Control Rules

1. **Committed repo docs, contracts, JSON catalogs, accepted mockups, tests, and code should become the durable source of truth.** Current code/contracts and the newest dated accepted docs win when older restart or tactical notes conflict, with discrepancies recorded rather than silently blended. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`.
2. **ChatGPT, Work, and Codex tasks are input and decision channels, not durable product memory.** An isolated task recollection must not authorize implementation. Source: `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`.
3. **External UI design-lab files remain design inputs until decisions and implementation contracts are integrated into the repo.** The lab may be newer, but recency does not make it canonical. Source: `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`.
4. **Generated mockups and prototypes are evidence, not implementation authorization.** They demonstrate report shapes and interaction ideas but do not automatically define navigation, object lifecycle, or production code. Source: `docs/project_control/ARRANGER_DOCUMENTATION_INVENTORY_v1.md`.
5. **Accepted decisions should be recorded in project-control docs.** The blueprint should update or supersede the decision register and create a repo-canonical implementation contract before wiring begins. Sources: `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md` and `C:/Users/fotto/cursor/Arangur UI Design Lab/ARANGUR_UI_DESIGN_LAB_INSTRUCTIONS.md`.
6. **Future Codex prompts must read the canonical workflow catalog, acceptance status, project-control packet/dossier, relevant app contracts/code, and accepted design contract together.** They must treat unresolved candidates as candidates, not fill gaps with extra UI. Source: `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`.
7. **Do not implement from isolated thread memory or mix tranches.** UI blueprint, UI wiring, local Docker polish, deployment planning, control-plane design, and private-data architecture remain separately gated work. Source: `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`.

## 11. Immediate Next Tranche: Advisor Workflow UI Integration Blueprint v1

### Controller-ready briefing

**Purpose**

Produce one repo-canonical product/UI contract that reconciles the current advisor app, four committed workflow families, accepted report/attribution architecture, and design-lab inputs before any UI wiring. The blueprint must make unresolved decisions explicit and testable. Sources: `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md` and `docs/project_control/ARRANGER_PROJECT_CONTROL_DOSSIER_v1.md`.

**Required inputs**

- This packet and the five companion project-control documents plus the machine inventory.
- `docs/product/report_workflow_catalog_v1.md`, `docs/product/report_family_acceptance_status_v1.md`, and the five JSON files in `data/simulation/report_workflows/demo_workflows_v1/`.
- Current lifecycle/UI evidence: `docs/demo/advisor_report_workflows.md`, relevant `docs/ui_reporting/` models, `src/arangur/app/static/index.html`, generated-report service/model contracts, and focused UI tests.
- Accepted report mockups and external story translation pack.
- All eight design-lab Markdown files and two source-inspected prototypes.
- Deployment/private-demo documents only as constraints; no deployment changes.

**Decisions the blueprint must make**

1. Select Briefing Desk, Arangur Guide, Investment Library, or an explicitly justified alternative; do not silently hybridize.
2. Define canonical internal and user-facing vocabulary for workflow, template, briefing, report set/view, generated report, advisor review, client preview, presentation, and evidence.
3. Define the object lifecycle, including whether a reusable definition and dated generated output are the only user-facing objects, how current-data generation behaves, and when durable history is added.
4. Specify the first screen and dominant action; map the four workflow families into business-language choices.
5. Bound custom creation in v1: edit approved templates, create reusable templates, or both.
6. Define distinct Builder, Advisor Review, Client Preview, Presentation, Historical Reading, Evidence, and Developer / QA state contracts.
7. Create a visibility/gating matrix for every canonical workflow step.
8. Define external-story caveat placement, candidate-proxy privacy, and first-release audience.
9. Decide which Plan Check/Objective Horizon and breadth-test rules are blueprint requirements versus deferred visual refinement.
10. State the design-lab stage gates required before UI wiring and the Frank approval gate.

**What the blueprint should produce**

- Approved vocabulary and object/lifecycle diagram.
- Selected application architecture with rationale against the six user jobs and recorded rejected/deferred alternatives.
- First-screen/chooser contract and business-language mapping for all four workflows.
- Screen/state map with one job, dominant action, visible information, hidden information, and transitions per state.
- Template/custom-creation scope and field contract.
- Advisor-review/client-preview/presentation visibility matrix.
- Ordered flow contract for each workflow, including accepted, supporting, advisor-only, setup, internal-control, diagnostic, optional, gated, and superseded treatment.
- Evidence, caveat, readiness/error, immutable-history, and Developer / QA boundaries.
- Design-lab acceptance/rejection/defer table.
- Focused implementation acceptance criteria and tests for the later wiring tranche.
- Project-control updates recording Frank-approved decisions.

**How to use the workflow catalog**

Treat the four workflow JSON files as the canonical ordered-content and visibility source. Translate their IDs and artifact paths into business labels; do not change report math or invent missing outputs. Preserve gate reasons, optional dense steps, and client/advisor distinctions. Source: `data/simulation/report_workflows/demo_workflows_v1/`.

**How to use the UI design lab**

Use the lab as design evidence and a set of alternatives. Preserve its six user jobs, one-action/progressive-disclosure rules, immutable-history proposal, evidence return path, selected Plan Check scope, Objective Horizon refinement boundary, and report breadth rules. Do not treat any application architecture or global visual system as selected. Source: `C:/Users/fotto/cursor/Arangur UI Design Lab/`.

**External-story treatment**

Keep External Manager Story Translation advisor/internal until Frank explicitly approves broader exposure. Show translated/not verified/not endorsed/not a recommendation status; keep candidate proxies internal; leave portfolio-through-lens and scenario outputs gated until their method, data, shape, and approval exist. Sources: `data/simulation/report_workflows/demo_workflows_v1/external_manager_story_translation_v1.json` and `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`.

**Advisor/client treatment**

Advisor surfaces may compose, reorder, review caveats, manage visibility, and inspect exact evidence. Client preview must reproduce the approved client sequence and language. Presentation must hide authoring, generation, export/setup, and administrative controls; it must preserve fixed dates, Next, contextual Explain/Evidence, and exact return. Sources: `docs/ui_reporting/briefing_set_client_preview_model_v1.md` and `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_client_report_how_am_i_doing_packet_v1.md`.

**Out of scope**

No production UI wiring, analytics changes, deployment work, live/real data, new math, internal control-plane studio, private-data topology implementation, or production-grade rendering/persistence. The blueprint may record future requirements without implementing them. Source: `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`.

## 12. Do-Not-Build-Yet List

Unless Frank explicitly changes direction, the blueprint and immediately following Advisor Workflow UI Wiring v1 should not build:

- AWS, Lightsail, Cloudflare, DNS, or other deployment changes.
- Docker/deployment configuration changes or deployment rehearsal as part of UI design/wiring.
- Real Plaid or custodian integration.
- Real client holdings, identifiers, or client data.
- New scenario math, probabilistic range engine, or new scenario-basis calculations.
- New attribution math, timing attribution, dollar P&L attribution, or production/client attribution claims.
- Position-level drill-down or full Manager-by-Manager Driver Detail with Position Drilldown.
- Internal analytics studio/control-plane UI.
- Production benchmark/proxy approval workflow or internal governance studio.
- Production pricing or market-data integration.
- Blended/all-in advisor-and-manager attribution.
- Full production client-report rendering/export/share engine; reuse current synthetic rendering for wiring tests.
- Durable production history/persistence merely to make the prototype feel complete, unless the approved blueprint explicitly creates a separate persistence tranche.
- Current-versus-proposed portfolio analytics.
- Investment recommendations, trade/order execution, or autonomous advisor actions.
- A silently hybridized Briefing Desk/Guide/Library architecture.
- A frozen global visual system based only on Objective Horizon.

Sources: `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`, `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`, and `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`.

## 13. Items Requiring Frank Review

Priority order reflects what most directly blocks an implementation-ready blueprint.

1. **Application architecture:** Which center of gravity should lead—Briefing Desk, Arangur Guide, Investment Library, or a separately specified alternative? If a hybrid is desired, which tested job failure justifies each borrowed behavior?
2. **Canonical vocabulary:** Which words should ordinary advisors see for the reusable definition, ordered conversation, dated output, and individual content step? Specifically resolve `workflow`, `briefing template`, `briefing`, `report set`, `report view`, and `generated report`.
3. **First screen:** Should entry ask what conversation the advisor needs, open a recent briefing, accept a guide request, or start from a collection? What is the one dominant action?
4. **Object lifecycle:** Are reusable template and immutable dated briefing the only visible saved objects? Does “use current data” always create a new briefing? Is durable backend history part of the next wiring tranche or a later persistence tranche?
5. **Custom creation scope:** Does v1 permit only use/duplicate/edit of approved templates, creation of new reusable templates, or both? Which business fields are allowed?
6. **Advisor review versus client preview:** What is the default rule for `advisor_review` steps? Must an advisor explicitly promote each step, or does each workflow ship with approved defaults? Is Client Preview a separate state from Presentation?
7. **External Manager Story Translation audience:** Is it advisor/internal only in the first release? Can an investment committee see the translation setup artifacts? Who can approve candidate proxies later?
8. **External-story caveat presentation:** Which caveat is persistent at chooser, review, preview, and evidence depths without overwhelming the interface?
9. **Client-report design scope:** Should the blueprint refine Plan Check/Objective Horizon only as a presentation contract, or include new visual mockup/prototype work before wiring? Confirm that Objective Horizon remains unfrozen globally.
10. **Design stage gates:** Which of the lab’s required artifacts—simplification audit, approved screenshots, prototype test results, and final implementation contract—must be completed before Advisor Workflow UI Wiring v1?
11. **Client objectives and thresholds:** Where do return/growth/cash/risk objectives come from, and what must the UI say when they are absent? Confirm that current illustrative values are not product defaults.
12. **Attribution depth:** How much advisor policy and manager mandate detail is client-accessible by default for sophisticated-client/committee workflows, and what remains advisor-only?
13. **Gated-step visibility:** Should gated steps remain visible to advisors in the ordered journey, and which reason categories are useful without creating a readiness-report substitute?

Sources: `docs/project_control/ARRANGER_UI_DESIGN_INPUTS_DIGEST_v1.md`, `docs/project_control/ARRANGER_NEXT_PHASE_INTEGRATION_QUEUE_v1.md`, `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`, and `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_interaction_directions_v1.md`.
