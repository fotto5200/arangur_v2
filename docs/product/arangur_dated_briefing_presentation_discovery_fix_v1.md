# Arangur Dated Briefing Presentation Discovery Fix v1

Status: implementation audit and corrected product contract
Date: 2026-07-16
Product: Arangur

## Scope

This bounded correction makes Advisor Review, Ready to Present, Audience Preview, Presentation, Resume, Find, and home shortcuts read the same normalized browser-local Dated Briefing records and the same deterministic eligibility rules. It does not redesign Briefing Section visuals, add analytics, add dependencies, change deployment, or create production persistence.

## 2026-07-16 advisor-selection extension

`docs/product/arangur_presentation_section_selection_and_audience_flexibility_v1.md` replaces the audience-restriction portion of this contract. The shared discovery architecture remains, but the shared sequence is now the advisor's saved presentation selection. Audience classification sets recommended defaults, not a prohibition. Reviewed plus at least one selected populated presentable section plus no true blocker is Preview eligible; Ready remains an explicit transition and implies Preview and Presentation eligibility. Protected internal and unavailable material cannot enter the saved sequence.

## Record and storage audit

Current Dated Briefings are stored under `arangur.local_briefings.v1` in a payload containing `schema_version` and `briefings`. A current record contains:

- identity and source: `briefing_id`, title, Briefing type ID/name, source Briefing Plan ID/name/kind;
- dates: generated/briefing date, data-as-of date, last activity, review, ready, preview, and presentation times;
- audience: saved audience, `advisor_internal_default`, and the saved journey's `audience_visibility` values;
- rendered content: immutable `advisor_artifact` and optional `client_artifact`, each with `ordered_sections`; populated sections have `status: rendered` and non-empty HTML;
- lifecycle: `review_status`, `status_model_version`, and presentation position/progress fields;
- gating: record-level `blocking_condition` (and compatible blocking-reason aliases), plus non-record-blocking journey-step availability explanations;
- compatibility/diagnostics: storage source/version and runtime normalization notes.

Related browser-local collections are:

- `arangur.local_named_briefing_workflows.v1` for reusable saved Briefing Plans;
- `arangur.local_briefing_plan_drafts.v1` for unfinished plans;
- `arangur.local_generated_reports.v1` for the earlier generated-report shelf, retained as Legacy and not silently converted into Dated Briefings.

## Lifecycle and filter audit

Before this correction:

- `normalizeBriefingRecord` normalized storage fields and promoted every earlier `reviewed` record without the current status-model marker to `ready_to_present`;
- `briefingDisplayStatus` trusted that normalized status and could display Ready to Present;
- `audienceVisibleSections` considered only rendered, non-empty `client_artifact.ordered_sections`;
- `isPreviewEligible` separately required reviewed/ready status, audience sections, and no `blocking_condition`;
- `isPresentationEligible` separately required ready status and preview eligibility;
- home Ready to Present, Choose/Open, and Launch used a ready-list wrapper; Preview filtered again; Resume added a last-presented check; Find searched all records but exposed only a generic open action;
- the presentation reader used `client_artifact || advisor_artifact`, a different sequence rule from eligibility;
- review and presentation transitions mutated the current in-memory object and wrote local storage, but there was no single normalized record commit helper or focused eligibility diagnostic.

## Root cause

Readiness was represented by a stored/displayed status and then independently requalified by screen-specific filters. The legacy migration promoted status alone, without proving an audience-visible populated sequence or absence of a blocking condition. A migrated record could consequently display Ready to Present elsewhere while Ready, Preview, Launch, and Resume excluded it. The presentation reader's advisor-artifact fallback was an additional sequence mismatch: content could be renderable by one surface without being recognized by shared eligibility.

The static tests asserted the presence of helper names and filter calls, but did not exercise record normalization and all presentation entry points as one lifecycle. That allowed the contradiction to survive.

## Corrected shared rule

All screens use normalized stored records and these shared concepts:

1. Reviewed means Advisor Review was completed or is safely recognized from compatible stored lifecycle evidence.
2. Audience-visible populated sections come from the saved client/audience artifact, or from an explicitly saved presentation-visible sequence for advisor/internal material. They must be rendered and non-empty.
3. A record-level blocking condition prevents Preview readiness and Presentation readiness. A gated journey step that is excluded from the audience sequence is not automatically a record-level block.
4. Reviewed + at least one audience-visible populated Briefing Section + no blocking condition = Preview eligible.
5. Ready to Present is accepted only when Preview eligibility is true.
6. Presentation eligible is the same Ready-to-Present rule; therefore presentation eligibility always implies Preview eligibility.
7. Resume additionally requires actual saved presentation progress.

Earlier two-state `reviewed` records are promoted to Ready to Present only when the stored artifacts prove the corrected shared rule. Explicit but contradictory legacy readiness is downgraded to Reviewed (or In Review when review evidence is absent) with a Developer / QA migration note. Records are retained and identifiers are not replaced.

## Audience behavior

- Client material uses Client Preview.
- Manager discussion material uses Manager Preview.
- Other explicitly audience-presentable material uses Audience Preview.
- Advisor/internal material without an explicit presentation-visible sequence may be Reviewed but cannot be marked Ready to Present.

## Persistence and refresh behavior

Review, readiness, preview, launch, progress, and resume mutations are committed through one normalization/upsert path. The same `briefing_id` is replaced in the in-memory collection and the full normalized collection is immediately written to `arangur.local_briefings.v1`. Dependent home, list, and Developer / QA views read that same collection on route rendering and after reload; no divergent Dated Briefing copy is created.

## Compatibility implications

The storage key remains unchanged. Current records remain current. Compatible earlier records normalize safely from known lifecycle and blocking aliases. Uncertain records are preserved without fabricated readiness. The older generated-report shelf remains separate Legacy material. Developer / QA reports the normalization source, version, notes, eligibility counts, blocking reason, and resume availability; ordinary advisor surfaces do not expose raw IDs or technical eligibility fields.
