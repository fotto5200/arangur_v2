# Report Element Information Budget Contract v1

## Purpose

This is a non-binding design contract for future report-element input and view fixtures. It defines information-budget constraints so report elements answer clear client/advisor questions without becoming analytics dumps.

This contract does not implement code, change UI, add report views, generate analytics, add endpoints, alter Docker/deployment files, fetch data, or add dependencies.

Controlling rule:

```text
Each visible field must justify its placement on the screen.
```

## Required Report-Element Framing

Every future report-element fixture should be able to declare:

- `audience_tier`: `client_briefing`, `advisor_review`, `internal_analytics_review`, or `developer_qa`.
- `master_question_family`: `ownership_exposure`, `performance_plan`, `risk_downside`, or `positioning_forward_view`.
- `report_admissibility_sentence`: "This report helps [audience] answer [specific question] by showing [minimal evidence]."
- `visible_field_budget`: maximum headline metrics, table rows, paragraphs, caveats, top positions, and explanatory labels.
- `allowed_fields`: fields permitted in the selected audience tier.
- `advisor_only_fields`: fields that may appear in advisor review but not client briefing.
- `internal_only_fields`: fields that must not appear in client or advisor report views.
- `anti_clutter_checks`: checks that prevent duplicate labels, duplicate caveats, raw source paths, debug fields, and unnecessary tables.

If the admissibility sentence is weak, the element should not be rendered as a first-class report element yet.

## Audience Tier Field Policy

| Audience tier | Allowed fields | Advisor-only fields | Internal-only fields |
| --- | --- | --- | --- |
| `client_briefing` | Report title, one-sentence conclusion, 1-3 headline metrics, 0-5 comparison rows, material caveat | Top positions only if explicitly approved for the report, limited confidence detail | Raw ids, source paths, schema names, manifests, valuation traces, pricing function ids, reconciliation/debug fields |
| `advisor_review` | Diagnostic conclusion, 1-4 headline metrics, 0-8 rows, material review items, compact confidence/coverage detail | Full manager/account/sleeve drilldowns, top impacted positions, review queue snippets | Raw JSON, file paths, schema names, detailed model traces, internal construction controls |
| `internal_analytics_review` | Full analytic rows, coverage details, reconciliation, validation notes, source artifact references | Not applicable | Secrets, real credentials, unapproved raw client data |
| `developer_qa` | Schema names, fixture paths, validation details, route/local-storage behavior, debug outputs | Not applicable | Secrets, credentials, private keys, real client data |

## Default Visible Budgets

| Budget item | Client briefing default | Advisor review default | Internal/developer default |
| --- | --- | --- | --- |
| Headline metrics | 1-3 | 1-4 | As needed |
| Table rows | 0-5 | 0-8 | As needed |
| Caveats | 0-2 | 0-4 | As needed |
| Top positions | 0 by default, 5 only when approved | 0-5 | As needed |
| Paragraphs | 1-2 short paragraphs | 1-3 short paragraphs | As needed |
| Explanatory labels | 0-3 | 0-5 | As needed |

Budgets are limits, not goals. A report element that needs fewer fields should use fewer fields.

## Anti-Clutter Checks

Future report-view tests should consider checks like:

- No raw source file paths in client or advisor fragments.
- No `.json`, schema, manifest, registry, artifact, or valuation trace language in client fragments.
- No duplicate caveat text inside one element.
- No more than the audience tier's maximum visible caveats.
- No more than the audience tier's maximum visible rows unless the element is explicitly an advisor review table.
- No top-position table in client briefing unless the element declares an approved top-position purpose.
- No table and paragraph that repeat the same statement.
- No zero or immaterial impact rows unless their absence would mislead.
- No confidence/coverage detail unless it changes interpretation.
- No thesis-readiness artifact in client view except a short unavailable explanation.

## Suggested Fixture Metadata

Future input/view fixtures can include design metadata like:

```json
{
  "information_budget": {
    "audience_tier": "client_briefing",
    "master_question_family": "risk_downside",
    "report_admissibility_sentence": "This report helps the client understand the largest downside scenario by showing the scenario impact and the few managers that drive it.",
    "max_headline_metrics": 3,
    "max_table_rows": 5,
    "max_caveats": 2,
    "top_positions_allowed": false,
    "client_visible_fields": ["headline", "scenario_name", "impact", "impact_percent", "top_manager_rows", "material_caveat"],
    "advisor_only_fields": ["top_positions", "coverage_mix", "confidence_mix"],
    "internal_only_fields": ["source_bundle_manifest", "market_state_id", "valuation_trace"]
  }
}
```

This metadata is a design aid. It should not force UI changes by itself.

## Revaluation-Derived Output Constraints

Full revaluation outputs are internal analytics sources. They do not automatically become report content.

Client-facing defaults:

- Portfolio scenario impact may be visible when scenario risk is the question.
- Worst scenario may be visible in a compact cross-scenario summary.
- Top manager or sleeve contributors may be visible only when they help the explanation.
- Top impacted positions are hidden by default.
- Coverage/confidence appears only as practical interpretation guidance.

Advisor-review defaults:

- Manager, account, sleeve, coverage, confidence, and top-position detail may appear when relevant.
- Review-required positions should be prioritized by materiality.
- Thesis readiness should explain unavailable thesis reports without pretending attribution exists.

Internal-only defaults:

- Bundle manifests.
- Scenario indexes.
- Valuation coverage manifests.
- Pricing function assignments.
- Source file references.
- Raw reconciliation fields.
- Valuation traces.

## Report-System Redesign Addendum

Future report-element fixtures should also carry these design constraints when the report family requires them:

- `report_family_id`: stable id from the report family catalog.
- `representation_level`: direct security, fund/NAV position, manager-level sleeve, look-through holding, lens bucket, benchmark/proxy, or proposed allocation.
- `denominator_policy`: the denominator that makes visible rows comparable or additive.
- `category_system_id`: the single taxonomy, lens, manager grouping, geography system, benchmark map, or status taxonomy used by the table.
- `summary_or_detail_variant`: summary and detail should be separate report variants, not one expanding default report.
- `lens_assignment_status`: present when a report depends on selected lens buckets.
- `benchmark_map_status`: present when a report makes benchmark-relative claims.
- `visual_denominator_or_range`: present for chart-first reports so the visual has the same explicit denominator/range discipline as tables.
- `timing_attribution_gate`: present for performance attribution; timing can appear only when two clearly specified portfolio states, period history, and flow treatment make it measurable.

After Synthetic Attribution Report Mockups v1, `benchmark_map_status` is satisfied only for the local synthetic `attribution_v1` Integrated Performance Attribution, Manager Attribution, and Lens-Based Performance Attribution mockups that point to the pack's synthetic policy benchmark or lens-bucket proxy map. This does not satisfy production/client attribution, scenario-versus-benchmark, probabilistic range, or timing attribution gates.

After Attribution Methodology and Calculation Audit v1, future attribution fixtures should also declare `attribution_effect_provenance` for each visible effect and `manager_benchmark_basis` for each manager benchmark-relative row. Acceptable provenance values should distinguish calculated arithmetic, supplied synthetic input, supplied formula allocation, and residual reconciler. A visible `Not separately measured` field is acceptable only as an advisor/internal calculation-gap signal, not as a final client-facing answer.

After Synthetic Attribution Calculation Inputs v1, future local calculated attribution fixtures can source `attribution_effect_provenance`, selected-lens policy, theme benchmark weight states, grouped asset inputs, residual policy, and manager benchmark-basis fields from `data/simulation/attribution_prerequisites/synthetic_attribution_prerequisite_pack_v1/calculation_inputs/`. Report fixtures should stop using supplied fixed-share attribution allocations once calculated synthetic outputs exist.

After Calculated Synthetic Attribution Engine v1, calculated local synthetic attribution outputs exist under `data/simulation/attribution_calculated/synthetic_attribution_engine_v1/`. Future attribution report fixtures should source whole-portfolio attribution, theme benchmark detail, theme asset detail, manager attribution, residual policy, tie-outs, and readiness flags from that calculated output pack rather than the older supplied fixed-share attribution allocation fields. This does not satisfy production/client attribution, scenario-versus-benchmark, probabilistic range, proposed-allocation, or timing-attribution gates.

Additional anti-clutter checks:

- Do not mix asset type, manager/sleeve, lens/theme, and coverage/review statuses in one additive table.
- Do not show benchmark-relative, lens-bucket, cash-flow support, proposed-allocation, timing-attribution, or probabilistic range claims unless the matching data/analytics prerequisites are satisfied.
- Keep prior-period cash delivered and forward-looking cash support outlook as separate report shapes unless a future approved detail variant explicitly combines them.
- Do not use readiness artifacts as client-facing reports. They may explain why a report is unavailable.
- Visual-first reports must state the range, benchmark/proxy, horizon, and caveat needed to interpret the picture.
- Performance attribution visible labels should prefer Global benchmark, Theme benchmark, Manager Benchmark Return, Portfolio Return, Asset selection/sizing, and `Residual / unexplained`; do not show raw proxy ids, proxy-return labels, or strategy/lens-bucket construction language in product-facing mockups.
- Benchmark-relative attribution effects must not imply lower-level calculation unless the required benchmark portfolio, asset, weight, manager benchmark-basis inputs, and calculated engine outputs exist. For the local calculated synthetic path, prefer the calculated output pack over supplied allocation fields; if an effect is supplied for synthetic demo review, label or caveat that provenance instead of hiding it.
- Timing attribution should stay unavailable unless clean trade/holding history, flow treatment, and an approved timing method exist; residual may include unmeasured timing/data/flow/reconciliation effects but must not be labeled timing.

## Kill Switch

If a future report element cannot satisfy this sentence, it should be postponed:

```text
This report helps [audience] answer [specific question] by showing [minimal evidence].
```

If a visible field cannot satisfy this sentence, it should be removed:

```text
This item helps the reader understand [specific point] and removing it would lose [specific value].
```

When in doubt, simplify.
