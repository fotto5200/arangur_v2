# Report Element Template Catalog Contract

## Purpose

The report element template catalog is the static demo source of truth for report-element discovery. It describes what kinds of elements Arangur can add to a Client Briefing Set or Advisor Review Set, which branches and placements each element supports, and which configuration parameters are required after the user selects a template.

This contract is intentionally lightweight. The current implementation uses a JSON catalog plus standard-library validation under `src/arangur/report_elements/`. It does not introduce persistence, migrations, report generation, chart generation, or a frontend framework.

## Discovery Versus Configuration

Discovery inputs help narrow candidate report elements. Examples include search text, discovery tags, client questions, advisor review intents, category, and branch.

Discovery inputs usually should not become part of the final saved report spec. A saved spec should be built from the selected template plus the configuration fields required or allowed by that template, such as branch, placement, scope, lens, metric, scenario, display form, and any caveat or readiness metadata.

The browser composer should treat search text, category filters, guided filters, category shortcut buttons, and browse-all picker navigation as discovery controls only. Selecting a template starts configuration; it does not automatically add anything to a set.

## Template-Driven Configuration

The selected template controls the configuration form. The UI should not expose a universal report form with every possible field.

Expected behavior:

- Fixed template values, such as `fixed_metric` or `fixed_or_default_display`, should travel with the spec without becoming unnecessary user questions.
- Scenario fields should appear only when the selected template supports or requires a scenario.
- Scope, lens, metric, display, placement, and advisor internal purpose choices should be constrained by the selected template and current branch.
- Completion checks should follow the template's required parameters and scenario requirement.

## Template Fields

Each template includes:

- `element_id`: stable machine id.
- `title`: human-readable label.
- `short_description`: short discovery text.
- `category`: coarse grouping for catalog browsing.
- `supported_branches`: allowed branches, currently `Client Briefing` and/or `Advisor Review`.
- `supported_placements`: branch-to-placement mapping.
- `discovery_tags`: search/filter tags.
- `relevant_client_questions`: client briefing discovery prompts.
- `relevant_advisor_review_intents`: advisor review discovery prompts.
- `supported_scopes`: entity or portfolio slice options.
- `required_parameters`: configuration fields required after selection.
- `optional_parameters`: optional configuration fields after selection.
- `fixed_metric`: metric fixed by the template, or `null`.
- `supported_metrics`: allowed metric choices when the metric is not fixed.
- `supported_lenses`: classification/grouping options when applicable.
- `scenario_requirement`: `required`, `optional`, or `not_applicable`.
- `fixed_or_default_display`: default display form.
- `supported_display_forms`: allowed future rendering forms.
- `advisor_internal_purposes`: advisor-side purposes where relevant.
- `data_readiness_requirements`: data prerequisites.
- `completeness_checks`: checks that must be made visible before publication.
- `default_caveat_rules`: caveat behavior that should travel with the spec.
- `branch_notes`: optional branch-specific usage guidance.

## Branch Model

`Client Briefing` and `Advisor Review` are separate branches. A template may support one or both, and its placements can differ by branch.

Client Briefing placements are for client package material such as main presentation, speaker notes, analytical appendix, or support appendix. Advisor Review placements are for internal review material such as main advisor review, working notes, analytical appendix, or support appendix.

## Scope Versus Lens

Scope identifies the entity or portfolio slice being viewed, such as `Whole portfolio`, `All managers compared`, `Selected manager`, `Selected account`, or `Selected sleeve / mandate`.

Lens identifies how the selected scope is classified or grouped, such as `Sector`, `Theme`, `Asset class`, `Liquidity bucket`, `Data issue`, or `Manager role / mandate`.

Plain `Manager` is not a lens. Manager belongs in scope when the user is choosing a manager entity or comparing all managers. `Manager role / mandate` may be used as a lens because it classifies managers by role.

## Scenario Requirement Behavior

`scenario_requirement` controls whether a selected template needs a scenario before it can become a complete element spec:

- `required`: the spec must include `scenario_id`. `Scenario Impact by Manager` uses this mode.
- `optional`: the spec may include a scenario, but can be complete without one.
- `not_applicable`: scenario configuration should be skipped.

Scenario-dependent elements should also expose scenario completeness checks, including whether the scenario treatment is complete, how much is directly repriced, how much uses proxy/remainder treatment, human-review counts, and the scenario horizon where available.

## Narrative Elements And Ordered Set Compatibility

The current composer supports manual narrative elements alongside analytic, catalog-backed elements. Narrative elements include section titles, short explanations, transitions, discussion prompts, speaker notes, advisor working notes, diagnostic comments, follow-up items, and client-prep notes.

Narrative elements are not generated reports and do not require analytics. They should still be treated as first-class ordered set elements because they control the briefing sequence around analytic evidence.

Future implementations can model narrative elements as either:

- catalog-compatible templates with stable narrative template IDs; or
- a parallel narrative type registry that serializes into the same ordered set envelope as analytic elements.

Either approach should preserve common ordered-row fields such as element kind, target set or branch, title/type, placement, order, and editable content.

## Report Spec Serialization Expectations

A future saved set spec should serialize two ordered lists or one ordered list with target-set grouping:

- Client Briefing Set elements
- Advisor Review Set elements

Analytic report element specs should serialize:

- selected `element_id`
- branch and placement
- advisor internal purpose when branch is `Advisor Review` and the template uses it
- configured scope, lens, metric, scenario, and display form as required by the template
- caveat and completeness metadata needed for review
- template version or catalog version when durable metadata is introduced

Narrative element specs should serialize:

- stable narrative type
- target set or branch
- placement
- title/text fields required by the narrative type
- order within the set

Discovery-only inputs should be omitted unless a product decision later requires keeping them for audit or explanation.

## Deliberately Not Implemented Yet

This catalog contract does not implement:

- report generation
- chart generation
- saved report-element specs
- backend persistence for report specs
- durable export/import of frontend spec sets
- production authorization or client data models
- live Plaid, external APIs, vendor data, or real financial/client data
