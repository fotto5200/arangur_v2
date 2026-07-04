# Analytic Pack Contract v1

## Purpose

An analytic pack is a published Arranger product artifact. It bundles approved themes, classification lenses, scenarios, market-state transformation assumptions, data confidence rules, and report-element capability mappings so Arangur can consume them without exposing internal control-plane construction tools.

The controlling scenario methodology is full portfolio revaluation. Approved pack scenarios describe how to construct a complete scenario market state from a base market state. Scenario impact should come from valuing every position under the base market state, valuing every position under the scenario market state, and aggregating the differences after valuation.

The first contract is intentionally small. It defines component shape and validation expectations for synthetic demo fixtures. It does not implement scenario math, portfolio calculation, a pack-management API, or an Arranger Studio UI.

## Pack Components

An analytic pack contains these components:

- `pack_manifest`
- `theme_catalog`
- `classification_lens_catalog`
- `scenario_catalog`
- `scenario_shock_pack`
- `data_confidence_rule_catalog`
- `report_analytic_capability_map`

Each component should include a schema/version marker, the `pack_id`, a component type, and a list of records with stable ids. Component versions may change independently, but a manifest version is the published unit that Arangur should consume.

## Pack Manifest

Purpose: binds component files into one approved pack.

Required fields:

- `schema_version`
- `pack_id`
- `pack_version`
- `display_name`
- `description`
- `created_by`
- `created_at`
- `approved_at`
- `synthetic_demo_pack`
- `component_paths`
- `notes`

Example:

- `pack_id`: `arranger_demo_pack_v1`
- `pack_version`: `2026-07-03-demo-v1`
- `display_name`: `Arranger Demo Analytic Pack v1`

Versioning expectations: Arangur consumes a manifest version, not loose component drafts. Published manifests should only reference approved component versions.

Relationship to report elements: the manifest points to a report analytic capability map that tells existing Arangur report elements which pack choices they can use.

Deliberately not included: execution code, live-data configuration, secrets, advisor UI state, portfolio-specific results, or deployment settings.

## Theme Catalog

Purpose: defines approved thematic categories that can be used for exposure, concentration, overlap, and report narrative.

Required fields for each theme:

- `theme_id`
- `display_name`
- `description`
- `exposure_direction_notes`
- `example_position_tags`
- `advisor_description`

Example ids/names:

- `ai_infrastructure` / `AI Infrastructure`
- `rate_sensitivity` / `Rate Sensitivity`
- `private_market_liquidity` / `Private Market Liquidity`
- `energy_security` / `Energy Security`

Versioning expectations: theme ids should remain stable across pack versions unless the meaning changes materially. Display copy can evolve with a new component version.

Relationship to report elements: themes can be used by Concentration, Manager Comparison, Scenario Impact by Manager, and related future report elements where the template supports a theme lens.

Deliberately not included: advisor-created tags, security-level classifications for real holdings, or final exposure calculations.

## Classification Lens Catalog

Purpose: defines approved ways to group or interpret portfolio records.

Required fields for each lens:

- `lens_id`
- `display_name`
- `description`
- `allowed_scope`
- `categories`

Example ids/names:

- `theme` / `Theme`
- `manager_role_mandate` / `Manager Role / Mandate`
- `liquidity_bucket` / `Liquidity Bucket`
- `data_confidence` / `Data Confidence`

Versioning expectations: lens ids should stay stable where possible. Category additions should be versioned when they affect report behavior.

Relationship to report elements: lens ids map to template-supported lenses such as Theme, Liquidity bucket, Manager role / mandate, Asset class, and Data issue.

Deliberately not included: a user-editable classification UI, look-through machinery, or real-client classification records.

## Scenario Catalog

Purpose: defines approved advisor-readable scenario choices and the internal market-state construction method behind each choice.

Required fields for each scenario:

- `scenario_id`
- `display_name`
- `short_description`
- `advisor_story`
- `primary_drivers`
- `supported_horizons`
- `supported_report_elements`
- `caveats`

Example ids/names:

- `ai_chip_selloff` / `AI / Chip Selloff`
- `rate_shock` / `Rate Shock`
- `private_market_liquidity_freeze` / `Private Market Liquidity Freeze`
- `taiwan_disruption` / `Taiwan Disruption`

Versioning expectations: scenario ids should stay stable when the advisor-facing story is the same. Market-state construction, perturbation, expansion, or caveat changes should be published through a new pack or component version.

Relationship to report elements: Scenario Impact by Manager requires a scenario and a revaluation bundle produced from that scenario's complete market state. Other elements may optionally reference scenarios if their template supports them.

Deliberately not included: probabilities, forecasts, investment recommendations, or live market-data inputs.

## Scenario Shock Pack

Purpose: defines approved deterministic perturbation assumptions for each published scenario. These are inputs to scenario market-state construction, not direct position impact formulas.

Required fields for each shock:

- `scenario_id`
- `shock_id`
- `variable_shocks`
- `qualitative_assumptions`
- `confidence_level`
- `caveats`

Example:

- `scenario_id`: `ai_chip_selloff`
- `shock_id`: `ai_chip_selloff_demo_shock_v1`

Versioning expectations: shock ids should change when variable shocks or qualitative assumptions change. Scenario ids should reference valid entries in the scenario catalog.

Relationship to report elements: scenario-aware report elements consume scenario ids and calculation outputs derived from these shocks; they should not expose raw shock construction controls to advisors.

Deliberately not included: production valuation logic, live market data, or advisor-facing controls for editing market-state construction. Covariance, PCA, key-rate, or related methods may later exist only as internal inputs for expanding approved perturbations into complete scenario market states.

## Data Confidence Rule Catalog

Purpose: defines approved language and rule intent for valuation coverage, source readiness, substitute-input policy, and confidence treatment.

Required fields for each rule:

- `rule_id`
- `display_name`
- `applies_to`
- `confidence_effect`
- `advisor_language`

Example ids/names:

- `human_review_required` / `Human Review Required`
- `proxy_valuation` / `Proxy Valuation`
- `stale_or_private_mark` / `Stale Or Private Mark`

Versioning expectations: rule ids should be stable for recurring confidence conditions. Advisor language changes should be versioned when they affect client-facing report copy.

Relationship to report elements: Data Confidence Note and other readiness-aware elements can use these rules to explain confidence labels and caveats.

Deliberately not included: operational workflows for resolving data issues, credentials, source-system integrations, or real-client exception records.

## Report Analytic Capability Map

Purpose: tells Arangur which report elements can use which pack components and inputs.

Required fields for each capability:

- `report_element_id`
- `supported_themes`
- `supported_scenarios`
- `supported_lenses`
- `supported_scopes`
- `required_inputs`
- `unsupported_reason_if_any`

Example report element ids from the current catalog:

- `portfolio_status`
- `concentration`
- `scenario_impact_by_manager`
- `cash_generation_summary`
- `manager_comparison`
- `data_confidence_note`

Versioning expectations: capability mappings should change when report element contracts, supported scopes, supported scenarios, or required inputs change.

Relationship to report elements: this map is the compatibility bridge between approved analytic packs and the existing Arangur report element catalog.

Deliberately not included: report workflow order, generated report artifacts, report library/history records, UI panels, or portfolio-specific calculation outputs.

## Validation Expectations

At minimum, a contract validation pass should verify:

- Manifest and component files exist.
- Component files load as JSON.
- Ids are present and unique inside each component.
- Scenario shocks reference valid scenario ids.
- Capability map report element ids exist in the current report element template catalog when feasible.
- Synthetic demo packs mark `synthetic_demo_pack` as `true`.
- Component paths do not point outside the pack directory.

The current repo includes a lightweight standard-library validator at `src/arangur/analytics/analytic_pack_loader.py`. It validates the demo fixture pack, checks pack cross-references, and can summarize component counts without adding a JSON Schema dependency.

## Current Demo Application

The first application of this contract is `data/analytic_packs/arranger_demo_pack_v1/`. It is applied to the existing synthetic portfolio and scenario fixtures by `src/arangur/analytics/apply_demo_pack.py`.

The current proof outputs are deterministic synthetic artifacts. The corrected controlling design now requires future scenario impact outputs to be backed by full revaluation bundles: base market state valuation, scenario market state valuation, position-level differences, and post-valuation attribution by manager/theme/confidence. Themes remain attribution/reporting layers, not valuation substitutes. Confidence records should identify revaluation coverage limitations, substitute-input use, stale/private mark treatment, and review-required positions.

The generated proof outputs live under `data/simulation/analytics/`:

- `theme_exposure_summary.json`
- `manager_theme_overlap_summary.json`
- `scenario_impact_by_theme_manager.json`
- `data_confidence_map.json`
- `cross_scenario_resilience_summary.json`
- `analytics_output_index.json`

These outputs are deterministic synthetic analytics artifacts. The current repo also maps them into separate analytic report-element input payloads and rendered view fragments under `data/simulation/report_element_inputs/` and `data/simulation/report_element_views/` for Concentration, Manager Comparison, Scenario Impact by Manager, Data Confidence Note, and Portfolio Status. The local Advisor workflow now consumes the approved pack through curated template choices and committed analytic-derived fragments in Preview, Populate, and Present. This remains local/demo consumption only; it is not a backend pack-management API, production storage system, live data flow, or advisor-facing control-plane editor.

## Deliberately Not Implemented In v1

- Advisor-facing control-plane UI.
- Arranger Studio UI.
- Pack authoring workflow.
- Backend pack-management endpoints.
- Full revaluation scenario-engine implementation, covariance/PCA/key-rate expansion runtime, or simulation-kernel changes.
- Live Plaid, live market data, external APIs, real client data, secrets, or deployment configuration.
