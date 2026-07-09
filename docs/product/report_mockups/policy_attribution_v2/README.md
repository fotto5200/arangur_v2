# Advisor Policy Attribution v2 Report Mockups

These local product-review mockups show advisor policy attribution by manager/sleeve.
The primary report separates selected mandate, target weighting, and funding drift effects before manager implementation review.
They are not wired into Advisor Preview, Populate, Present, generated reports, Docker, deployment, live data, external data, or production reporting.

## Generated Mockups

- [Advisor Policy Attribution by Manager/Sleeve](advisor_policy_attribution_by_manager_mockup_v2.md)
- [Advisor Policy Effect Totals](advisor_policy_effect_totals_mockup_v2.md)

## Benchmark Basis

Both v2 mockups now show a compact Benchmark Basis section. The primary report names Synthetic Global Policy Benchmark and shows the global benchmark, neutral selected mandate basket, target policy benchmark, and actual allocation benchmark returns so selected mandate effect has a visible comparator.

## V1 Supersession

Policy-Level Attribution Summary v1 remains a local calculation reference, but it is superseded as the primary product-review surface.
Advisor Policy Attribution by Manager/Sleeve v2 is the primary review surface for advisor-level policy effects.

## Gated Or Deferred

- Manager / Within-Mandate Attribution Detail (Future tranche): Requires a separate manager-driver report using manager mandate responsibility.
- Blended / All-In Attribution (Deferred): Deferred so advisor policy and manager implementation stay separate.
- Timing Attribution (Unavailable): Unavailable because clean timing inputs and an approved method are absent.
- Dollar P&L Attribution (Gated): Gated unless reliable beginning portfolio value exists.
- Production Client Attribution (Gated): Gated on approved real policy targets and benchmarks.
- Current-vs-Proposed Policy Attribution (Gated): Gated on a proposed allocation workflow.
- Old Bridge Summary (Superseded): Superseded as the primary report surface by the manager/sleeve advisor policy report.
