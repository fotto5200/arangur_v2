# Advisor Workflow UI Visibility and Gating Matrix v1

Status: recommended product contract for Frank review; derived from the committed workflow JSON

## Legend

| Classification | Meaning | Default client behavior |
| --- | --- | --- |
| Client-facing | Accepted content intended for the named client audience. | Included after Advisor Review. |
| Advisor-review | Advisor decides whether/how it belongs in a client/committee conversation. | Hidden unless explicitly approved for that briefing. |
| Advisor-only | Oversight or analytical depth not intended for ordinary client delivery. | Hidden. |
| Setup/readiness | Establishes basis, coverage, or prerequisites. | Hidden unless the fact materially changes a client conclusion; then express a concise caveat rather than a readiness report. |
| Diagnostic | Calculation or drill-down support. | Hidden. |
| Internal-control | Reconciliation/governance control. | Hidden. |
| Optional | Accepted supporting depth invoked for the meeting/job. | Included only after explicit advisor choice. |
| Gated | Missing approved data, method, report shape, proxy/benchmark, or advisor approval. | No fabricated output; normally hidden. |
| Superseded | Retained only for calculation/history. | Never selectable as the primary surface. |

## Cross-surface rules

- **Ordinary Advisor UI** shows business titles, questions answered, visibility, optionality, and calm gate reasons.
- **Client Preview** contains exactly the reviewed client-visible sequence.
- **Presentation** contains the same content/order as Client Preview with authoring/admin chrome removed.
- **Developer / QA** may expose IDs, source paths, raw status, JSON, mockup/view links, and reconciliation data.
- A gated/readiness object never substitutes for the missing client answer.
- `accepted_with_minor_polish` is available for the documented synthetic demo but does not mean production approval.

## Principal / Family Office Briefing

Source: `data/simulation/report_workflows/demo_workflows_v1/principal_family_office_briefing_minimal_v1.json`.

| # | Step | Classification | Ordinary Advisor UI | Client Preview | Presentation | Developer / QA | Caveat/gate behavior |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | Portfolio Representation Status | Client-facing / primary | Show as opening context; flag material completeness. | Include. | Include conclusion-first. | Show IDs, source mockup/view, synthetic status. | Do not lead with technical coverage mechanics. |
| 2 | Cash Flow Delivered | Client-facing / primary | Show. | Include. | Include. | Exact source paths and calculations allowed. | Trailing delivery is not forward support. |
| 3 | Cash-Flow Support Outlook | Client-facing / primary | Show if required inputs exist. | Include. | Include. | Exact input/readiness detail allowed. | Do not manufacture cash need or horizon. |
| 4 | Coverage and Confidence Warning | Advisor-review / supporting / readiness | Show only material issues before approval. | Replace with adjacent concise caveat only when interpretation changes. | Same concise caveat; no standalone readiness report by default. | Full coverage/confidence detail. | `accepted_with_minor_polish`; advisor support, not client answer. |
| 5 | Aggregated Asset Allocation | Client-facing / supporting | Show. | Include. | Include at appropriate depth. | Exact mapping/source allowed. | Broad ownership only; avoid manager-detail overload. |
| 6 | Current Portfolio Scenario Downside | Client-facing / supporting | Show selected accepted scenarios. | Include. | Include with common base/scale/horizon. | Position valuation and assumptions allowed. | Deterministic result is not a forecast or probability. |
| 7 | High-Level Advisor Plan / Next-Year Positioning | Gated / handoff | Show restrained “Not ready — approved plan content is missing.” | Hidden. | Hidden. | Show gate ID and missing report shape. | No generated plan mockup; do not invent a recommendation. |

## Engaged Client / Investment Committee Review

Source: `data/simulation/report_workflows/demo_workflows_v1/engaged_client_investment_committee_review_v1.json`.

| # | Step | Classification | Ordinary Advisor UI | Client Preview | Presentation | Developer / QA | Caveat/gate behavior |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | Portfolio Representation Status | Client-facing / setup-readiness | Show as context and completeness check. | Include concise context. | Include only useful conclusion. | Full basis/source metadata. | Do not make readiness the meeting's main answer. |
| 2 | Policy Allocation Review | Client-facing / primary | Show. | Include. | Include. | Exact target/actual basis allowed. | State policy basis; imputed basis cannot be mislabeled. |
| 3 | Advisor Policy Attribution by Manager/Sleeve | Advisor-review / primary | Show with review marker. | Include only after advisor approval for this audience. | Same approved form; exact table may be available at Verify depth. | Full denominator/formula/source. | Keep selected mandate, target weighting, and funding drift separate. |
| 4 | Manager Mandate Attribution Summary | Advisor-review / primary | Show with review marker. | Include only after advisor approval. | Include conclusion; exact table at Verify depth when needed. | Full mandate basis and source. | Do not blend advisor and manager responsibility. |
| 5 | Full Lens Exposure — AI Adoption | Client-facing / primary | Show. | Include. | Include composition/exception conclusion. | Full classification mapping. | Review-required bucket remains explicit. |
| 6 | Full Lens Exposure — Energy Security | Client-facing / primary | Show. | Include. | Include composition/exception conclusion. | Full classification mapping. | One primary bucket per position per lens. |
| 7 | Manager by Lens Exposure — AI Adoption | Advisor-review / supporting | Show as optional supporting depth. | Hidden by default; include only for sophisticated audience after approval. | Same approved content. | Full manager denominators/mappings. | Manager rows use their stated denominator. |
| 8 | Current Portfolio Scenario Downside | Client-facing / primary | Show. | Include. | Include. | Full revaluation evidence. | Common base/scale/horizon; no probability claim. |
| 9 | Manager Driver Attribution Matrix | Advisor-review / optional supporting | Show as optional dense follow-up. | Hidden by default; include for committee reconciliation only. | Never a five-minute opening; exact table when selected. | Full stored-precision reconciliation. | `accepted_with_minor_polish`; portfolio-effect basis must be explicit. |

## Advisor / Manager Oversight

Source: `data/simulation/report_workflows/demo_workflows_v1/advisor_manager_oversight_v1.json`.

| # | Step | Classification | Ordinary Advisor UI | Client Preview | Presentation | Developer / QA | Caveat/gate behavior |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | Policy Allocation Drift Summary | Advisor-only / primary | Show exception-first. | Hidden. | Hidden. | Full source/basis. | Advisor decision, not manager failure. |
| 2 | Manager Mandate Benchmark Basis | Advisor-only / setup-readiness | Show only missing/changed basis prominently. | Hidden. | Hidden. | Full benchmark mapping. | No manager attribution without approved basis. |
| 3 | Advisor Policy Attribution by Manager/Sleeve | Advisor-review / primary | Show. | Not available from this advisor-only workflow by default. | Advisor/internal presentation only. | Full basis/source. | Separate from manager implementation. |
| 4 | Manager Mandate Attribution Summary | Advisor-review / primary | Show. | Hidden by default. | Advisor/internal only. | Full source/denominator. | Assigned mandate controls comparison. |
| 5 | Manager Driver Attribution Matrix | Advisor-only / primary | Show exact table when reconciliation is the job. | Hidden. | Advisor/internal only. | Full matrix/source. | All-manager portfolio-effect basis. |
| 6 | Within-Manager Attribution Detail | Advisor-only / diagnostic | Open from selected manager; preserve return. | Hidden. | Hidden from client; advisor-only presentation if explicitly needed. | Full selected-manager denominator/source. | No position-level extension in v1. |
| 7 | Manager Implementation Handoff | Internal-control / handoff | Hide from ordinary flow; show only explicit reconciliation detail. | Hidden. | Hidden. | Full tie-out. | Control artifact, not a product conclusion. |
| 8 | Coverage and Confidence Warning | Advisor-review / supporting | Show material evidence-quality issues. | Hidden unless later promoted as adjacent caveat in another client briefing. | Hidden by default. | Full coverage detail. | Does not substitute for report output. |
| 9 | Coverage/Confidence by Manager | Gated / diagnostic | Show restrained gate only if it helps completeness review. | Hidden. | Hidden. | Show missing data/report-shape reason. | No generated manager-sliced coverage report exists. |

## External Manager Story Translation

Source: `data/simulation/report_workflows/demo_workflows_v1/external_manager_story_translation_v1.json`.

Persistent surface caveat: **Translated from an external manager story. Not verified. Not endorsed. Not a recommendation. Candidate proxies require approval.**

| # | Step | Classification | Ordinary Advisor UI | Client Preview | Presentation | Developer / QA | Caveat/gate behavior |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | Manager Story Summary | Advisor-review / setup note | Show with persistent caveat. | Hidden in v1 unless Frank approves broader audience. | Advisor/internal only. | Source artifact and status allowed. | Summary does not validate the story. |
| 2 | Implied Lenses | Advisor-review / setup note | Show as candidate questions. | Hidden in v1. | Advisor/internal only. | Candidate IDs/mappings allowed. | Lenses are narrative-derived, not approved product lenses. |
| 3 | Key-Price Scenario Set | Advisor-review / setup note | Show as candidate scenario questions. | Hidden in v1. | Advisor/internal only. | Candidate assumptions/source allowed. | No live-data validation or forecast status. |
| 4 | Candidate Benchmark/Proxy Map | Internal-control / setup-readiness | Hidden from ordinary advisor path unless authorized proxy review is the job. | Hidden. | Hidden. | Show candidates and approval flags. | Every proxy is approval-required and not a recommendation. |
| 5 | Portfolio Through External Lens | Gated / primary | Show “Not ready — lens assignments and report shape are not approved.” | Hidden. | Hidden. | Full gate reason. | No fabricated exposure output. |
| 6 | Manager by External Lens | Gated / supporting | Show “Not ready — manager lens inputs/report shape are not approved.” | Hidden. | Hidden. | Full gate reason. | No fabricated manager output. |
| 7 | Scenario Downside under External Story | Gated / supporting | Show “Not ready — scenario inputs/report shape are not approved.” | Hidden. | Hidden. | Full gate reason. | No fabricated downside output. |
| 8 | Scenario by Lens | Gated / supporting | Show “Not ready — approved lens assignments and scenario aggregation are missing.” | Hidden. | Hidden. | Full gate reason. | Scenario-by-lens remains unavailable. |
| 9 | Governance/Caveat Note | Advisor-review / handoff | Show and require completion. | Hidden in v1; if future client use is approved, material caveat must travel with every affected claim. | Advisor/internal close. | Full governance artifact. | Caveat cannot be removed by template editing. |

## Superseded and diagnostic exclusions across workflows

| Item | Classification | Ordinary Advisor UI | Client Preview / Presentation | Developer / QA |
| --- | --- | --- | --- | --- |
| Policy-Level Attribution Summary v1 | Superseded | Not selectable as primary. | Hidden. | Retain as calculation/reference evidence. |
| Policy-Level Manager Effect Detail v1 | Superseded | Not selectable as primary. | Hidden. | Retain as calculation/reference evidence. |
| Equal-weight AI Adoption Attribution | Diagnostic unless explicit policy | Advisor-only with basis label. | Hidden unless equal weight is explicitly approved as policy and audience use is separately approved. | Full diagnostic allowed. |
| Integrated/lens attribution v1 diagnostics | Diagnostic | Hidden from default workflow chooser. | Hidden. | Available for validation. |
| Cash-Flow Support Readiness client shape | Superseded | Not selectable as client answer. | Hidden. | Retain historical/reference artifact. |
| Mixed-category concentration shape | Superseded | Not selectable. | Hidden. | Retain historical/reference artifact. |

## Gate reason codes for later wiring

| Internal reason code | Advisor-facing language | Client behavior |
| --- | --- | --- |
| `missing_data` | Not ready — required data is missing. | Hide; show a material caveat on affected accepted content if needed. |
| `missing_approved_method` | Not ready — the calculation method is not approved. | Hide. |
| `missing_report_shape` | Not ready — this briefing section has not been approved. | Hide. |
| `missing_benchmark_or_proxy` | Not ready — an approved benchmark or proxy is required. | Hide. |
| `awaiting_advisor_approval` | Needs advisor review before client use. | Exclude until approved. |
| `not_for_audience` | Advisor-only preparation content. | Hide. |

These codes are internal. Ordinary UI uses the language above and never exposes raw code values.
