# Policy Attribution v1 Report Mockups

These local product-review mockups are generated from Policy Attribution v1 view data backed by the synthetic policy/mandate pack.
They are not wired into Advisor Preview, Populate, Present, generated reports, Docker, deployment, live data, external data, or production reporting.

## Generated Mockups

- [Policy-Level Attribution Summary](policy_level_attribution_summary_mockup_v1.md)
- [Policy-Level Manager Effect Detail](policy_level_manager_effect_detail_mockup_v1.md)
- [Imputed Baseline Policy Attribution Variant](imputed_baseline_policy_attribution_variant_mockup_v1.md)

## Bridge Behavior

Policy-Level Attribution bridges Global benchmark -> Target policy benchmark -> Actual allocation benchmark -> Actual portfolio.
Policy allocation review remains allocation hygiene; this set separates return effects from target-versus-actual drift review.

## Gated Or Deferred

- Within-Manager Attribution Detail (Future tranche): Requires separate manager-driver report design and lower-level inputs.
- Blended / All-In Attribution (Deferred): Deferred until separate policy-level and manager-level reports are understood.
- Timing Attribution (Unavailable): Unavailable because clean timing inputs and an approved method are absent.
- Dollar P&L Attribution (Gated): Gated unless reliable beginning portfolio value exists.
- Production Client Attribution (Gated): Gated on approved real policy targets, real benchmarks, and production review.
- Current-vs-Proposed Policy Attribution (Gated): Gated on a proposed allocation workflow.
