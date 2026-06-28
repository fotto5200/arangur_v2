# Demo Console Redesign Brief v1

## Purpose

This brief translates the UI/reporting philosophy into a redesign direction for the current browser demo console.

The current console is technically useful but transitional. It proved that the working API integration can be reframed around client questions and briefing preparation, but it is too dense to be the target product surface.

Correction: the target UI is a guided briefing builder, not a fuller briefing console. See `docs/ui_reporting/guided_briefing_builder_correction_v1.md` and `docs/ui_reporting/client_briefing_page_model_v1.md`.

## First Screen Layout

Original transitional console concept:

1. Header: `Arangur v2 Briefing Room`
2. Primary control: `Client question`
3. Secondary control: `Audience depth`
4. Optional advisor control: `Source`
5. Action: `Prepare briefing`
6. Briefing preview:
   - Plain-English answer
   - Key evidence
   - Interpretation
   - Proposed action
   - Confidence and caveats
7. Evidence/drill-down:
   - Report links
   - Data coverage links
   - Internal run detail in Advisor/Internal mode

Corrected sparse first screen:

1. Product title or working title.
2. One-sentence purpose.
3. Compact synthetic/local demo caveat.
4. Current step label.
5. One primary decision: `Client question`.
6. Continue action.

Audience depth, source context, suggested evidence bundle, advisor notes, client briefing preview, appendices, and technical/admin details should appear only after the relevant step.

## Visible Labels

Use:

- `Client question`
- `Audience depth`
- `Prepare briefing`
- `Plain-English answer`
- `Key evidence`
- `Confidence and caveats`
- `Advisor-only details`
- `Open briefing report`

Avoid:

- `Workflow`
- `Run pipeline`
- `Analytics module`
- `Raw outputs`
- `Source adapter` as a first-screen primary label

Also avoid on the first screen:

- Raw report links.
- JSON links.
- Recent run history.
- Technical/demo panels.
- Full caveat blocks.
- Report directory behavior.

## Source And Workflow Mapping Strategy

The guided builder can still use existing APIs internally:

- Client question maps to an internal workflow type.
- Audience depth maps to presentation defaults.
- Source remains available as an optional secondary control.
- The app still calls `POST /api/runs`.
- The returned run summary still provides report links and evidence metadata, but those should be shown in later evidence or technical/admin layers rather than the first screen.

Example mapping:

| Client question | Internal workflow |
| --- | --- |
| Are we on track? | `quarterly_review` |
| Where are we too concentrated? | `manager_overlap_review` |
| What could hurt us? | `scenario_risk_review` |
| Why do we own Manager 5? | `manager_overlap_review` plus manager-role framing |
| What needs verification? | `data_coverage_review` |

## Report Section Hierarchy

Briefing reports should lead with:

1. Client question
2. Plain-English answer
3. Key evidence
4. Interpretation
5. Proposed action
6. Confidence and caveats
7. Drill-down / appendix

Existing analytics sections can become evidence and appendix material.

## Advisor-Only Versus Client-Facing

Advisor-only by default:

- Source adapter.
- Workflow type.
- Run ID.
- Raw JSON links.
- Data-quality debug details.
- Unsupported-methodology notes.

Client-facing by default:

- Client question.
- Plain-English answer.
- Evidence cards.
- Interpretation.
- Advisor-approved follow-up questions.
- High-level confidence and caveats.

## Guided Builder Correction

The prior `Arangur v2 Briefing Console` implementation is an implementation baseline, not the final interaction model.

The next UI should replace the dense console with a stepwise builder:

1. Choose client question.
2. Choose audience depth.
3. Choose portfolio/source context.
4. Review suggested briefing bundle.
5. Add/remove supporting briefing cards.
6. Review advisor draft.
7. Open client briefing.

Each step should introduce one clear choice and collapse previous choices into a compact summary. The first screen must stay sparse.

## Main-Path Exclusions

The main guided-builder path should not show these on the first screen:

- Raw report links.
- JSON links.
- Report package links.
- Recent run history.
- Technical details.
- Demo mechanics.
- Full caveat blocks.
- Report directory behavior.
- Local report index links.

These belong in a technical/admin appendix or report browser.

## Surface Separation

Future UI implementation should distinguish:

- Advisor guided builder: stepwise composition and advisor review.
- Client briefing page: answer-first, client-ready summary.
- Evidence appendix: support material for briefing cards.
- Technical/admin appendix: workflow IDs, run IDs, JSON/report links, artifact paths, and report history.

## First Implementation Phases

Phase 1:

- Add static mapping from client questions to workflow types.
- Rename the primary UI control to `Client question`.
- Add audience depth selector with `Standard Family Office Meeting` as default.
- Keep optional source selector secondary.

Phase 2:

- Replace the dense one-page console with the sparse guided builder sequence.
- Move raw run history, artifact links, and technical panels into a technical/admin appendix.
- Preserve selected question, audience, and context in a compact summary.

Phase 3:

- Add advisor draft review and a separate client briefing page.
- Add manager-role review path for "Why do we own Manager 5?"
- Add manager comparison cards using current manager/exposure outputs where possible.
- Add placeholders for mandate metadata not yet implemented.

Phase 4:

- Add audience-depth-aware report generation and report package metadata.
- Separate client briefing export from advisor/internal appendix.

## Implementation Baseline

Implemented 2026-06-28 as a dependency-free static browser console served from `/`, `/app/`, and `/app/index.html`.

The current baseline keeps the existing API behavior and maps visible client questions to internal workflow types in frontend JavaScript. Audience depth is displayed in the prepared briefing and recent briefing context when captured by the browser, but backend report packages do not yet persist client question or audience-depth metadata.

This baseline is functional but too dense. It should be treated as a transitional console and replaced by a sparse guided builder before deeper UI polish.

Sparse guided builder replacement implemented 2026-06-28. The current static browser app now steps through client question, audience depth, portfolio context, suggested briefing bundle, advisor draft, and client briefing, with evidence/advisor/technical appendices hidden until requested.
