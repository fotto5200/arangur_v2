# Arangur UI Blueprint Frank Review Items v1

Status: prioritized approval queue for `Advisor Workflow UI Integration Blueprint v1`

The blueprint is complete as a review draft. No advisor-facing UI wiring should begin until the blocking decisions below are approved or revised.

| Priority | Decision needed | Recommended answer | Alternatives and consequences | Blocks UI wiring? |
| ---: | --- | --- | --- | --- |
| 1 | Application architecture | Approve **Conversation Briefing Desk**: business-conversation chooser first; dated briefing becomes the center after generation. | Pure Briefing Desk weakens first-time/job entry; free-form Arangur Guide adds interpretation risk; Investment Library makes objects/collections primary. A different named composite requires an explicit job/behavior map. | Yes |
| 2 | Canonical vocabulary | Use **Briefing type** for the four built-ins, **Briefing template** for reusable definitions, and **Briefing** for dated immutable outputs. Keep `workflow` and `generated report` internal/legacy. | Keeping Workflow visible is technically direct but conflicts with design principles. Keeping Generated Reports preserves current UI but weakens template/output identity. | Yes |
| 3 | First screen | Approve “Prepare a briefing” / “What conversation are you preparing?” with four Briefing types and one **Continue** action; prior briefings and template management are secondary. | Recent-document opening favors repeat presentation; library entry favors retrieval; guide prompt favors free text. Each changes the application's center of gravity. | Yes |
| 4 | Object lifecycle | Approve two saved user objects: reusable Briefing template and immutable dated Briefing. Current-data use always creates a new briefing. Durable backend history is a later tranche. | Mutable reports weaken historical trust. Adding a report-set/conversation object creates a third lifecycle. Building durable persistence now expands scope into tenancy/retention/audit. | Yes |
| 5 | Custom creation scope | Approve built-in use plus duplicate/edit/save-as-custom; defer ordinary from-scratch creation. | Built-ins only is simpler but limits advisor authorship. From-scratch preserves current power but risks recreating an unconstrained report console. | Yes |
| 6 | Advisor Review / Client Preview defaults | Keep them separate. `advisor_review` steps are excluded from Client Preview until explicitly approved for that briefing; Presentation exactly matches Client Preview content/order. | Automatic inclusion simplifies use but risks leakage. Combining Preview and Presentation reduces states but mixes rehearsal and audience delivery. | Yes |
| 7 | External story audience and caveats | Advisor/internal only in v1. Persist “translated, not verified, not endorsed, not a recommendation; proxies require approval.” Lock governance fields. | Committee/client exposure before approval increases endorsement risk. A dismissible one-time disclaimer is too weak. | Yes |
| 8 | Plan Check / Objective Horizon scope | Keep Plan Check limited to the first client “How am I doing?” story. Continue Objective Horizon refinement without freezing a global visual system. | Global adoption now would force inappropriate forms onto scenario, lens, cash, and attribution jobs. Reopening Wealth Journey/Stewardship Brief delays selection. | Yes for visual wiring; no for nonvisual lifecycle work |
| 9 | Design stage gates | Require approved architecture, vocabulary/lifecycle, state map, visibility matrix, simplified target-state mockups, focused disposable prototype, and recorded prototype results before production UI wiring. | Waiving mockup/prototype gates accelerates code but asks implementation to resolve design gaps. | Yes |
| 10 | Client objective sourcing | Require validated client return/growth/cash/risk objectives before “on plan” language. When absent, show precise outcome language and “objective not recorded,” never design-only defaults. | Using illustrative 6.5%, 4.0%, ±3 pp, or -15% values as defaults creates false client facts. | Yes for Plan Check conclusions |
| 11 | Attribution depth visibility | Principal workflow excludes dense attribution. Engaged Client/Committee requires advisor approval for advisor/manager summaries; Driver Matrix is optional committee depth. Oversight remains advisor-only. | Broad client inclusion raises complexity and responsibility/denominator confusion; hiding all attribution underserves sophisticated committees. | Yes |
| 12 | Gated-step visibility | Advisors see gated steps only when they clarify workflow completeness; clients do not. Use calm reason language and never a readiness artifact as the client answer. | Hiding all gates can obscure advisor completeness. Showing them to clients creates promises and clutter. | Yes |

## Requested Frank response format

For each priority, record **Approve**, **Revise**, or **Defer**, plus replacement wording where revised. Approval should be copied into the project-control decision register before `Advisor Workflow UI Wiring v1` begins.

## Nonblocking follow-ups after approval

- Exact visual styling, typography, and motion within approved states.
- Durable history storage/retention design.
- Future free-form Guide research.
- Future portfolio/library retrieval architecture at production scale.
- Internal control-plane and private-data execution architecture.
