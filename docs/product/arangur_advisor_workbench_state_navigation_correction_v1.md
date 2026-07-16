# Arangur Advisor Workbench State and Navigation Correction v1

Status: implemented local product contract
Date: 2026-07-16
Product: Arangur

## Decision

The accepted Advisor Workbench information architecture remains unchanged. This correction makes object identity, selection feedback, lifecycle status, comparison, and return navigation coherent without redesigning populated Briefing Sections.

## Selection feedback

- The Briefing Section stage always separates **Included in this Briefing Plan** from **Available Briefing Sections**.
- The included group shows order, audience/advisor visibility, required or optional status, configured summary, and Remove where permitted.
- The available group shows the business question, purpose, visibility, availability/gate state, and Add.
- Add immediately moves the section into Included, updates an accessible live selected count, and updates the persistent **Current Briefing Plan** outline.
- Remove immediately returns an optional section to Available and updates the count and outline.
- A catalog entry already represented in the plan cannot be added twice. Intentional duplication remains a later Order & visibility action with a distinct section identity.
- Selection is communicated by placement, labels, button state, outline, and `aria-live` status rather than color alone.

## Configuration clarity

Sections with supported choices show the section name, current selection, and a plain-language explanation of what changes affect. Sections without supported choices are labeled **No choices needed** and do not open a dead-end editor. Back returns to the selected-section stage, and all choices persist in the Draft.

## Briefing Plan Draft identity

A persisted Draft carries a meaningful temporary or advisor-supplied name, Draft label, audience, created and last-edited timestamps, exact builder stage, selected-section count, Autosaved status, and source template when present. Temporary names are audience-aware:

- Untitled Client Briefing Plan;
- Untitled Advisor Briefing Plan;
- Untitled Manager Discussion Plan.

Repeated temporary names receive a sequence. A Draft is not persisted merely because setup or customization was opened. Persistence begins after a meaningful field edit, section addition, or advance beyond initial setup. Continue restores the exact stage. Rename is non-destructive. Discard Draft requires confirmation and no Draft is silently deleted.

## Saved Briefing Plan identity

A saved plan displays name, audience, saved and last-edited times, source lineage, section count, and the latest Dated Briefing created from it where present. Ordinary actions are Revise, Duplicate, Create Dated Briefing, and Archive. Drafts and saved plans remain separately labeled. Archive retains the browser-local record while removing it from ordinary active lists.

## Dated Briefing identity

Generation presents an editable, meaningful title suggestion before creating the immutable object. The suggestion combines audience, purpose, and date and is disambiguated when necessary. Lists show title, audience, briefing date, data date, source Briefing Plan, displayed status, section count, and latest review or presentation activity.

## Status model and transitions

One displayed lifecycle controls ordinary actions:

1. **Briefing Plan Draft** — unfinished reusable intent; Continue Plan.
2. **Saved Briefing Plan** — completed reusable intent; Revise or Create Dated Briefing.
3. **Dated Briefing** — immutable populated output in Advisor Review; View or Complete Advisor Review.
4. **Reviewed** — Advisor Review explicitly completed; Client, Manager, or Audience Preview is available when an audience-visible rendered sequence exists.
5. **Ready to Present** — Reviewed, previewable, and free of a blocking condition; Preview and Present.

Earlier browser-local `reviewed` records from the prior two-state model normalize to Ready to Present so compatible history is not stranded.

## Advisor Review completion

**Complete Advisor Review** is explicit. It requires at least one populated Advisor Review section and no stored blocking condition. Completion records `reviewed_at`. Optional advisor-only material does not need to become audience-visible. A separate **Mark Ready to Present** action is available only when Preview eligibility is true.

## Audience Preview and Presentation

Preview is advisor rehearsal of the exact audience-visible rendered sequence. Its label is Client Preview, Manager Preview, or Audience Preview according to the saved audience, and it retains **Back to Advisor Review**.

Presentation is clean audience delivery. A Dated Briefing is presentable only when its status is Ready to Present and the same record is previewable. Advisor/internal Briefings without an audience-visible sequence may become Reviewed but do not appear in Preview, Ready, Launch, or Resume lists.

The Ready, Preview, Launch, Resume, Find, and home shortcuts all read the same browser-local Dated Briefing records and shared eligibility functions.

## Navigation return context

Major workbench routes use an explicit parent route. Ask Arangur stores Ask as the return route when it sends the advisor to another workbench destination. Dated Briefing View and Advisor Review retain their source list or shortcut.

Presentation stores a return context with source route, Dated Briefing ID, Briefing Section index, origin, and the record's presentation position. Next/Previous updates that same context. Exit restores the same Dated Briefing and same section in Audience Preview. Resume reopens the saved record and saved section position. Browser history is not used as the object identity source.

## Dated Briefing comparison

Comparison is an explicit four-step sequence: select first, select second, review selection, then click **Compare Briefings**. Selecting the second item does not run comparison.

The result shows both titles and dates, common sections, sections unique to each, supported saved configuration/visibility changes, and limitations. With no common section it states: **These Dated Briefings do not contain comparable Briefing Sections.** It lists both unique sets and recommends selecting Briefings from the same or a similar plan. Historical positions, unrecorded values, and unsupported analytics are never inferred or fabricated.

## Empty states

Ordinary empty states name the missing object or eligibility and provide a next action. They avoid raw gates and include No Briefing Plan Drafts, No Dated Briefings to Compare, No Ready-to-Present Briefings, and No Audience Preview Available.

## Compatibility and preserved capabilities

The four top-level activities, Recent Work, Ready to Present, Recent Dated Briefings, Ask Arangur, subordinate Developer / QA, all three advanced builder paths, catalog/parameters, add/remove/reorder/duplicate, immutable generation, Advisor Review, audience filtering, Presentation, Explain/Verify, history, legacy normalization, external-story governance, calm gates, and browser-local persistence remain.

## Explicit deferral

This tranche does not redesign populated Briefing Sections, import design-lab HTML, add analytics, change calculations, or invent values. The next visual tranche remains **Arangur Dated Briefing Reader and Design-Lab Visual Integration v1**.
