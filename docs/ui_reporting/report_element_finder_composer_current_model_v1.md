# Report Element Finder / Composer Current Model v1

## A. Overview

Arangur now has a dependency-free browser Report Element Finder / Composer for assembling local report element specs into two ordered sets:

- `Client Briefing Set`
- `Advisor Review Set`

The current model is:

```text
compact context
-> target set
-> report element finder
-> template preview
-> template-specific configuration
-> add configured analytic or narrative element to an ordered set
```

This is a spec-composition surface, not a report generator. The UI helps an advisor choose which report elements belong in a briefing package or advisor review package, configure only the fields required by the selected element, and arrange analytic and narrative elements in a local ordered list.

The current catalog is static/mock and served through `/api/report-elements`. Configured elements remain local browser state. They are not serialized, exported, persisted, rendered into charts, or connected to report generation yet.

## B. Current User Workflow

1. Confirm client context.

   The current page starts with a compact static context line for the demo client, portfolio state, data status, and review count. The context is intentionally quiet because this composer is about choosing report elements, not running a portfolio workflow.

2. Choose target set.

   The advisor chooses either `Client Briefing Set` or `Advisor Review Set` before discovery. This choice controls which catalog templates are eligible, which placements are available, and which narrative element types make sense.

3. Find a report element template.

   Discovery happens through search, category browsing, guided filters, category shortcut pills, and the compact grouped `Browse all templates` picker. Discovery should feel like finding a useful element, not filling out a universal report form.

4. Preview template.

   Selecting a candidate template opens the existing selected-template preview. The preview explains the template, summarizes what the UI will ask for, and leaves the advisor in control through `Use this element`.

5. Configure template-specific fields.

   After `Use this element`, the selected template determines the configuration fields. The composer should only ask for the parameters required or allowed by that template, such as placement, scope, lens, scenario, selected metric, or advisor internal purpose.

6. Add configured element to set.

   A complete configuration becomes a compact local spec row in the chosen ordered set. The row represents a report element request, not a generated report artifact.

7. Optionally add narrative elements.

   The advisor can add manual narrative/text elements such as section titles, short explanations, transitions, discussion prompts, speaker notes, working notes, diagnostic comments, follow-up items, and client-prep notes.

8. Reorder, edit, duplicate, or remove elements.

   Both analytic and narrative rows live in the same ordered set lists. Rows can be edited, duplicated, moved up or down, or removed. Advisor Review analytic rows may expose a promote-to-client placeholder, but Client Briefing and Advisor Review should still remain separately authored artifacts.

## C. Client Briefing Set vs Advisor Review Set

`Client Briefing Set` is the client-facing or client-supporting package. Its elements should be selected and phrased for a meeting-ready client conversation. It may include main presentation material, speaker notes, client analytical appendix items, and support appendix material.

`Advisor Review Set` is the internal working package. Its elements can support preparation, diagnostics, caveat review, data readiness, follow-up planning, or internal interpretation before client material is approved.

The two sets should not automatically move in lockstep because they serve different jobs:

- A useful advisor diagnostic may be too technical or preliminary for a client package.
- A client-facing explanation may need supporting advisor notes that should not be shown to the client.
- The same analytic template may require different placement, purpose, or caveat treatment in each set.
- Promotion from advisor review to client briefing should be a deliberate advisor action, not an automatic mirror.

## D. Discovery vs Configuration

Discovery choices help the advisor locate templates. They include search text, category, guided filter, category shortcut, and browse-all picker selection.

Discovery choices are not automatically saved in the final report element spec. They are pathfinding metadata. The durable spec should be built from:

- selected template identity;
- chosen target set or branch;
- placement;
- template-required configuration fields;
- template-allowed optional fields when the advisor sets them;
- completeness, caveat, and readiness metadata when future serialization supports it.

For example, an advisor may find `Scenario Impact by Manager` by searching for "risk" or using a scenario filter. The saved spec should record the selected template and configured scenario, not the incidental search query that found it.

## E. Template-Specific Configuration

The catalog-driven composer must not show one universal configuration form for every element.

The selected template determines which fields appear:

- A template with a fixed metric should not ask the advisor to choose a generic metric.
- A template with `scenario_requirement = not_applicable` should skip scenario fields.
- A template that requires a scenario should block completion until a scenario is selected.
- A template that supports Advisor Review internal purposes can ask for that purpose only in Advisor Review context.
- A template with supported scopes, lenses, or display forms should expose only the meaningful choices for that element.

This keeps the UI sparse and reduces invalid combinations. The advisor configures the report element they selected, not an abstract reporting engine.

## F. Scope / Lens / Scenario Distinctions

These three concepts must stay separate.

`scope` means whose portfolio slice or entity is being viewed.

Examples:

- Whole portfolio
- All managers compared
- Selected manager
- Selected account
- Selected sleeve / mandate

`lens` means how positions or entities are classified, grouped, or interpreted.

Examples:

- Sector
- Theme
- Asset class
- Liquidity bucket
- Data issue
- Manager role / mandate

`scenario` means a hypothetical future pricing or risk environment applied to the portfolio.

Examples:

- AI/chip selloff
- Rates up
- Liquidity stress
- Other future scenario-library entries

Plain `Manager` is not a lens. Manager belongs under the scope or entity axis when the advisor is choosing a manager or comparing all managers. `Manager role / mandate` can be a lens because it classifies managers by their intended role.

This distinction matters because `Selected manager by theme under AI/chip selloff` and `All managers compared by manager role / mandate with no scenario` are different report specs.

## G. Metric / Measure Distinction

Many templates have a fixed measure. The composer should not expose a generic metric picker unless the selected template truly supports or requires that choice.

Examples:

- A cash generation element may have a cash or liquidity measure fixed by the template.
- A scenario impact element may have scenario impact fixed as the measure.
- A data confidence note may focus on confidence/readiness rather than portfolio value.

When a template has `fixed_metric`, that fixed measure should travel with the spec without becoming an advisor question. When a template has `supported_metrics`, the UI can expose a controlled metric choice.

The product language should prefer `measure` or `focus measure` when explaining what an element actually computes or emphasizes. `Metric` remains acceptable as a catalog field name, but the UI should avoid turning every element into an open-ended metric selector.

## H. Display and Formatting

Display form is usually fixed or defaulted by the template. It should not become a universal front-door choice.

Examples:

- A status element may default to a compact status card.
- A comparison element may default to a table-like view.
- A scenario element may default to an impact summary.

Future formatting choices such as theme, chart density, table styling, slide layout, audience depth, page numbering, or export style belong at a later set-level presentation/settings layer. They should not clutter the main element composer unless a selected template has a real display choice that affects the meaning of the element.

## I. Narrative Elements

Briefings are not just analytics. Advisors need text and structure around the evidence.

Narrative elements belong in the same ordered set lists as analytic elements because they control the actual briefing sequence:

- Section titles create meeting structure.
- Short explanations provide plain-English framing.
- Transitions connect one analytic view to the next.
- Discussion prompts turn evidence into advisor-led conversation.
- Speaker notes help the advisor present client-facing material.
- Working notes and diagnostic comments support internal review.
- Follow-up items and client-prep notes capture next actions without implying automated recommendations.

Narrative elements should be visually distinct from analytic elements but should share row operations: edit, duplicate, move, and remove. They should not call AI, generate text automatically, or trigger report generation in the current demo.

Longer-term, narrative types can be represented as catalog-compatible templates or a parallel narrative registry. Either way, a serialized briefing set should preserve their order alongside analytic specs.

## J. Current Demo Limitations

The current demo has important boundaries:

- No report generation from configured sets yet.
- No charts from configured sets yet.
- No client preview from configured sets yet.
- No persistence, save/load, export, or import for the composed sets yet.
- No backend briefing-set object yet.
- No AI discovery, AI drafting, or AI narrative generation yet.
- Static/mock report element template catalog for now.
- Synthetic/demo data only.
- Existing workflow report generation remains separate from this composer.
- No live Plaid, external APIs, real client data, credentials, or production authorization behavior.

The composer can create local specs that look like the right future object shape, but they are not durable and do not drive reporting yet.

## K. Next Actions

Likely next batches:

1. Serialize/export completed Client Briefing Set and Advisor Review Set specs.

   Define a stable local JSON shape for ordered analytic and narrative elements without generating reports. This should capture selected template IDs, target set, placement, configured parameters, narrative fields, order, and enough catalog/version metadata for future compatibility.

2. Add backend persistence later.

   After the export shape is stable, add a demo-safe backend persistence path for saved briefing sets. Keep this distinct from workflow-run persistence.

3. Build client preview later.

   Render the Client Briefing Set sequence as a client-facing preview only after the selected spec list can be represented consistently.

4. Connect configured specs to report generation later.

   The reporting pipeline should eventually consume configured specs, but that is a separate contract and implementation batch. It should not be smuggled into the composer.

5. Add AI assistance later for discovery and narrative framing.

   AI can eventually suggest templates, draft narrative framing, or propose set order. The current product stance remains: AI proposes, Arangur computes, advisor approves.
