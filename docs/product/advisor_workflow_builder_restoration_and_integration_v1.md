# Advisor Workflow Builder Restoration and Integration v1

Status: implemented local product contract
Date: 2026-07-15
Product: Arangur

## Decision

Arangur keeps the Conversation Briefing Desk as the ordinary advisor entry and restores advanced authoring through progressive disclosure. The restoration is part of the same product lifecycle, not a separate composer product:

> Briefing type → reusable briefing template → current-data briefing → Advisor Review → Client Preview → Presentation → immutable history

## Three supported paths

1. **Use illustrative as-is.** Choose a built-in, inspect its reusable journey, confirm current synthetic context, and create a new dated briefing.
2. **Deeply customize illustrative.** Choose **Customize this template**, then move through Purpose, Reports, Configure, Order & visibility, and Preview. Saving creates a custom reusable definition; the built-in remains unchanged.
3. **Start from scratch.** Choose **Build a custom briefing template** on the Desk, select a briefing type for audience/governance bounds, and start with no sections. The same five stages and downstream briefing lifecycle apply.

The first path stays short. The second and third reveal builder power only after explicit advisor intent.

## Builder stages

| Stage | User job | Product behavior |
|---|---|---|
| Purpose | Name the reusable conversation | Capture template name, audience/depth, purpose, and material notes/caveats |
| Reports | Decide what the conversation should answer | Search/filter business-language reports; show family, question, purpose, availability, and visibility; add supported reports or an advisor note |
| Configure | Make only supported choices | Show catalog-defined scope, lens, metric, scenario, period, threshold, focus, placement, and related approved choices where applicable |
| Order & visibility | Shape the conversation | Reorder, duplicate, remove, and mark permitted sections client-visible; never promote advisor-only or gated work |
| Preview | Inspect the reusable definition | Show purpose, audience, exact order, configuration summaries, visibility, optionality, and caveats before save/create |

## Catalog integration

The builder catalog combines two committed sources already used by the app:

- the selected business workflow's accepted, available, setup, gated, and deferred journey definitions from `/api/briefing-templates`; and
- the configurable six-element report catalog from `/api/report-elements`.

Workflow entries preserve business titles, visible questions, inclusion purposes, status, and audience visibility. Configurable entries preserve the report-element contract and approved analytic-pack enumerations. Superseded reports do not become selectable primary content. Gated/deferred entries may be visible as explanatory, disabled placeholders, but cannot be added as generated results.

## Lifecycle and object boundaries

- A **briefing template** is reusable and mutable. Built-ins are read-only; customization begins from a copy.
- A **dated briefing** is populated from a template and the current fixed synthetic snapshot. Creation always adds a new browser-local record.
- **Advisor Review** contains the complete ordered journey and unavailable-step explanations.
- **Client Preview** contains only accepted client-visible generated sections.
- **Presentation** uses the same client-visible sequence and excludes internal controls and unavailable output.
- **History** keeps prior dated briefings immutable. Editing a template never changes history.

## Compatibility

The browser continues to use `arangur.local_named_briefing_workflows.v1` for reusable local templates and `arangur.local_briefings.v1` for dated briefings. On edit, earlier named-workflow records are normalized from client-only, advisor-only, or mixed spec-set shapes into one editor sequence; missing local section identity, titles, parameter containers, status, and visibility metadata receive safe runtime defaults. The saved payload remains in the established client/advisor spec-set shape.

Internal IDs, storage keys, schema versions, rendered-view matching, JSON transfer, and migration notes remain in Developer / QA. Ordinary advisor and client surfaces use business language.

## Design-lab integration

The implementation promotes these design-lab principles into the canonical product contract:

- one dominant action per stage;
- progressive disclosure without capability removal;
- a conclusion-first report surface;
- Understand/Conclusion → Explain → Verify → exact return to the same section;
- cash as answer plus bridge, scenario as a stable bounded comparison, lenses as part-to-whole, and attribution as exact reconciliable evidence;
- no prototype-only objectives, thresholds, tolerances, ranges, or scenario values become defaults.

Plan Check remains limited to the first client-facing “How am I doing?” story. Objective Horizon remains a preferred refinement input, not a global app architecture or source of client facts.

## Governance boundaries

- External Manager Story Translation remains advisor/internal by default and visibly translated, not verified, not endorsed, and not a recommendation; candidate proxies require approval.
- No report is made available merely because a design prototype contains a visual for it.
- No new analytic math, probability, threshold, benchmark, proxy, client objective, or factual claim is created in the builder.
- The UI remains synthetic-demo only, local, and private.

## Acceptance

Acceptance requires all three builder paths, simple lifecycle continuity, catalog/configuration behavior, compatibility, external-story boundaries, Explain/Verify return, Developer / QA separation, automated full discovery, and local browser walkthroughs to pass. Evidence is recorded in `docs/demo/advisor_workflow_builder_integrated_demo_v1.md`.
