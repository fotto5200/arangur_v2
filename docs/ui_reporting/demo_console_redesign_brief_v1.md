# Demo Console Redesign Brief v1

## Purpose

This brief translates the UI/reporting philosophy into a redesign direction for the current browser demo console.

The current console is technically useful but transitional. The next version should preserve the working API integration while leading with client questions and briefing preparation.

## First Screen Layout

Proposed first screen:

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

## Source And Workflow Mapping Strategy

The redesigned UI can still use existing APIs internally:

- Client question maps to an internal workflow type.
- Audience depth maps to presentation defaults.
- Source remains available as an optional secondary control.
- The app still calls `POST /api/runs`.
- The returned run summary still provides report links and evidence metadata.

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

## First Implementation Phases

Phase 1:

- Add static mapping from client questions to workflow types.
- Rename the primary UI control to `Client question`.
- Add audience depth selector with `Standard Family Office Meeting` as default.
- Keep optional source selector secondary.

Phase 2:

- Add briefing preview structure above raw run history.
- Map returned run summaries into evidence cards.
- Hide raw artifact links unless in Advisor/Internal mode.

Phase 3:

- Add manager-role review path for "Why do we own Manager 5?"
- Add manager comparison cards using current manager/exposure outputs where possible.
- Add placeholders for mandate metadata not yet implemented.

Phase 4:

- Add audience-depth-aware report generation and report package metadata.
- Separate client briefing export from advisor/internal appendix.

## Implementation Baseline

Implemented 2026-06-28 as a dependency-free static browser console served from `/`, `/app/`, and `/app/index.html`.

The current baseline keeps the existing API behavior and maps visible client questions to internal workflow types in frontend JavaScript. Audience depth is displayed in the prepared briefing and recent briefing context when captured by the browser, but backend report packages do not yet persist client question or audience-depth metadata.
