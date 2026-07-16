# Advisor Workflow Builder Parameter Contract v1

Status: implemented local contract
Date: 2026-07-15
Product: Arangur

## Rule

The advisor builder may expose a parameter only when the committed report-element catalog declares it and the application already has a bounded, approved choice set. Fixed measures and display forms remain fixed. Free-form analytics construction is not an advisor capability.

## Shared parameters

| Parameter | Advisor label | Source of choices | Behavior |
|---|---|---|---|
| `branch` | Visibility branch | Briefing type and client-visible control | Derived; never displayed as an internal enum |
| `placement` | Advisor Review placement | Catalog `supported_placements` | Selectable where a configurable element supports Advisor Review |
| `scope` | Scope | Catalog `supported_scopes`, narrowed to honest preview support | Required where declared |
| selected entity | Selected manager/account/sleeve/strategy | Existing synthetic demo entity lists | Required only for a selected-entity scope; never a real client lookup |
| `lens` | Lens / manager role / data confidence lens | Approved analytic pack or catalog `supported_lenses` | Never offers plain “Manager” as a lens |
| `metric` | Measure / compare by | Catalog `supported_metrics` | Hidden when the metric is fixed |
| `scenario_id` | Scenario | Approved analytic pack scenario choices | Required or optional exactly as declared; unsupported rendered combinations remain unavailable |
| `theme_focus` | Theme focus | Approved analytic pack theme choices | Optional where declared |
| `confidence_focus` | Confidence focus | Existing bounded confidence choices | Optional where declared |
| period/focus fields | Period, comparison period, horizon, threshold, cash need, comparison group, review focus | Existing `PARAMETER_UI` enumerations | Optional only for the report elements listed below |
| fixed measure/display | Measure/display summary | Catalog `fixed_metric` and `fixed_or_default_display` | Preserved in the saved configuration; not freely editable |

`audience_depth` is captured at the reusable-template level because it governs the whole conversation. `confidence_note` is represented through template notes/caveats or a narrative section rather than treated as free-form analytic input.

## Configurable report elements

| Report | Required advisor choices | Supported optional choices exposed | Fixed behavior |
|---|---|---|---|
| Portfolio Status | placement, scope | comparison period; template-level audience/depth and notes | fixed catalog display |
| Concentration | placement, scope, lens, metric | theme focus, threshold, comparison period, optional approved scenario overlay | catalog display forms only |
| Scenario Impact by Manager | placement, scope, scenario | optional lens, horizon, scenario note where bounded | fixed Scenario impact measure |
| Cash Generation Summary | placement, scope | optional lens, cash need, period, approved scenario only when supported | fixed catalog display |
| Manager Comparison | placement, scope, manager-role/mandate lens, metric | theme focus, comparison group, mandate note | catalog display forms only |
| Data Confidence Note | placement, scope, data-confidence lens | confidence focus and review focus | fixed Data confidence measure |

The staged UI exposes every catalog-declared analytic choice that has a bounded approved enumeration, including full supported scopes and selected-entity choices, optional lenses and scenarios, and all bounded `PARAMETER_UI` fields. `audience_depth` remains at template level and `confidence_note` remains a template/narrative caveat, so neither is converted into an unrestricted analytic text box. Compatible saved records preserve those fields when already present.

## Workflow-catalog report sections

Accepted workflow reports such as Portfolio Representation Status, Cash Flow Delivered, Cash-Flow Support Outlook, Current Portfolio Scenario Downside, Policy Allocation Review, Advisor Policy Attribution by Manager/Sleeve, Manager Mandate Attribution Summary, and Full Lens Exposure use their committed workflow definition. They can be selected and ordered when available, but they do not gain synthetic configuration controls that their contract does not define.

Supporting, setup/readiness, advisor-only, diagnostic, gated, and deferred entries retain their committed status and visibility. Gated/deferred entries remain disabled explanatory catalog rows or intended journey placeholders; the builder does not manufacture output.

## Validation

1. Values must come from the catalog, approved pack, or existing synthetic demo enumerations.
2. A selected-entity scope must have the corresponding selected entity.
3. Required scenarios must use an approved scenario name.
4. A selection without a committed rendered match may be saved as a reusable intent but generates an honest unavailable placeholder.
5. Client visibility must also pass briefing-type and report-visibility bounds.
6. Configuration summaries in template preview must use plain labels, not parameter keys.

## Explicit exclusions

The builder must not expose or infer:

- design-lab sample objectives, tolerances, return targets, drawdown limits, funded-status thresholds, probability bands, or sample ranges;
- new scenario shocks, probabilities, forecasts, or valuation methods;
- unapproved benchmarks or proxies;
- control-plane construction, pack publishing, raw JSON, schemas, source paths, run IDs, or renderer settings;
- live or real client data.
