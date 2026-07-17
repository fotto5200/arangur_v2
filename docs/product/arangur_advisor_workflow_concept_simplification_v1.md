# Arangur Advisor Workflow Concept Simplification v1

Status: implemented local product contract
Date: 2026-07-16
Product: Arangur

## Decision

The ordinary advisor lifecycle is:

> Briefing Plan → Create Dated Briefing → View Dated Briefing → Present Dated Briefing

Arangur does not expose a separate user-visible concept unless it solves an ordinary advisor problem. The advanced builder, stored records, immutable generation, history, presentation section selection, presentation progress, legacy normalization, and Developer / QA diagnostics remain intact.

This contract supersedes mandatory Advisor Review, Preview, Prepare for Presentation, and Ready-to-Present gating in the ordinary UI. Compatible fields and routes may remain internally.

## Simplified home

The ordinary home has exactly four primary activities:

1. Prepare a New Briefing Plan
2. Work with Existing Plans or Briefings
3. Present a Dated Briefing
4. Ask Arangur

Recent Work and Recent Dated Briefings are small secondary shortcuts. Recent Work favors Drafts and recently edited saved Plans so Dated Briefings are not repeated under nearly identical shortcut labels. Recent Dated Briefings offers Open and, when the record has a selected populated sequence, Present. Developer / QA remains a subordinate footer action.

## Prepare a New Briefing Plan

Prepare contains only:

- **Build from Scratch** — audience, purpose, depth, and selected Briefing Sections lead into the full five-stage builder.
- **Start from a Template** — opens one library containing Arangur Example and My Saved Plan sources, with audience, purpose, included sections, approximate depth, Use, and Customize.

Prior Plans and unfinished Drafts remain accessible from the unified Existing library rather than appearing as additional Prepare choices. The four illustrative workflows remain example templates rather than product categories.

## Unified Existing library

Work with Existing Plans or Briefings opens one mixed, clearly labeled library. The selected object determines its actions:

| Object | Ordinary actions |
| --- | --- |
| Draft | Continue, Rename, Discard |
| My Saved Plan | Revise, Duplicate, Create Dated Briefing, Archive |
| Dated Briefing | Open, Create Updated Dated Briefing, Present |

Create Updated Dated Briefing recovers the source Plan, applies the current synthetic data snapshot through the existing generation flow, creates a new immutable record, and preserves the earlier Dated Briefing. If an older record's source Plan no longer exists, Arangur recovers a revisable Plan before generation rather than fabricating configuration.

Comparison remains implemented for compatibility and Developer / QA investigation but is absent from ordinary menus and routes.

## Single Present flow

Present a Dated Briefing opens one searchable Dated Briefing list. Search covers available client/audience, manager, date, and source Plan metadata. Selecting a row opens the same Dated Briefing reader used elsewhere.

The selected Dated Briefing shows its first actual populated presentable Briefing Section, Previous, Next, current position, a compact section agenda, Choose Sections, Present Briefing, and Back. Selecting, inspecting, and presenting are one flow. There is no required ordinary Preview state and no separate Choose, Preview, Start, Resume, or Find menu.

Presentation starts at the first selected section, uses the saved/default sequence, provides Previous, Next, position, and Exit, and returns to the same Dated Briefing and section. Existing progress fields remain compatible but Resume is not a primary product activity.

## Presentation section selection

All populated presentable Briefing Sections are selected by default. Protected internal and unavailable items are excluded. Audience classification remains available as an optional recommendation, not a prohibition and not the default exclusion rule.

Choose Sections is optional. It supports include, exclude, reorder, and save. An existing explicit custom selection is preserved. If an older record has no explicit saved selection, normalization derives the full populated presentable sequence. A changed selection resets presentation progress without changing the immutable content.

## Presentation availability

The ordinary governing rule is:

> At least one selected populated presentable Briefing Section → Present Briefing is available

Review status, Ready-to-Present status, preview history, and obsolete blocking/readiness fields do not gate ordinary presentation. Protected classifications and unavailable output remain outside the sequence by construction.

Old review/readiness fields, normalization notes, stored blockers, Preview decisions, and Resume diagnostics may remain visible in Developer / QA for compatibility audits.

## Dated Briefing reader

Opening a Dated Briefing is content-first. It does not initially show Plan setup metadata, section definitions, report-purpose descriptions, readiness rules, eligibility explanations, workflow internals, raw IDs, schemas, or JSON. The populated Briefing Section visuals themselves are not redesigned in this tranche.

## More Detail

Explain and Verify are not universal ordinary actions. A Briefing Section may show **More Detail** only when an explicit genuine supporting-content payload exists, such as a calculation bridge, assumptions, benchmark basis, component breakdown, caveat, manager/position detail, or detailed table. Generic prose, report definitions, raw JSON, schema fields, unapproved mappings, and synthetic placeholder explanations do not create More Detail.

Attribution Briefing Sections keep their exact reconciliable tables directly visible and do not add a redundant More Detail step.

## Ask Arangur

Ask Arangur is one prompt experience with a small set of example requests. Deterministic local routing can open Prepare, Existing, Present, a Plan, a Dated Briefing, or product help. It does not claim a live external AI connection, make investment recommendations, invent data, or bypass governance.

## Compatibility and Developer / QA boundary

Arangur preserves the existing browser-local Draft, Plan, Dated Briefing, presentation-selection, presentation-order, presentation-progress, template-lineage, generated-report, and legacy storage collections. Records are normalized on read and never silently deleted.

Developer / QA may show IDs, storage versions, old statuses, Preview/Presentation/Resume decisions, selected section IDs, blockers, raw metadata, normalization notes, migration status, and comparison diagnostics. Those concepts remain subordinate and do not compete with ordinary advisor activities.

## Preserved capabilities

The advanced Briefing Plan builder, supported catalog and parameters, add/remove/reorder/duplicate, audience/visibility defaults, template customization, immutable Dated Briefing creation, history, external-story governance, protected technical classification, exact selection/order persistence, presentation navigation, exit context, Ask Arangur routing, legacy compatibility, and Developer / QA remain.

## Deferred reader and visual work

This tranche does not redesign populated Briefing Section visuals, import Design Lab HTML, add analytics, change calculations, fabricate data, add comparison to ordinary UI, add persistence infrastructure, or change deployment.

Recommended next tranche: **Arangur Dated Briefing Reader and Design-Lab Visual Integration v1**.
