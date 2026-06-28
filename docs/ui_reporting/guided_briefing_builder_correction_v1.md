# Guided Briefing Builder Correction v1

## Purpose

This document corrects the next UI direction after the first `Arangur v2 Briefing Console` implementation.

The current browser console includes the right concepts: client questions, audience depth, source choice, briefing preparation, evidence links, confidence, recent briefings, and technical details. The problem is not that those concepts are wrong. The problem is that they appear together too early.

The target UI is not a briefing console. The target UI is a guided briefing builder.

## Core Correction

Arangur should not feel like an encyclopedia of reports, a brokerage dashboard, or an operations console. It should feel like a guided process for composing the right client conversation.

The advisor should not land on a page that shows every report type, evidence category, artifact link, caveat, technical detail, and recent run at once. That satisfies requirements mechanically but weakens the product metaphor.

The corrected mental model is:

```text
One clear question -> one clear audience -> one clear context -> one curated bundle -> one client-ready briefing.
```

## Why The Current Console Is Too Dense

The current briefing console is useful as a transitional proof that the API and report artifacts can support a browser surface. It is too dense as a product direction because it:

- Shows setup controls, evidence summaries, report artifacts, caveats, recent briefings, boundaries, and technical details on the same initial page.
- Makes generated artifacts feel like the product instead of support material behind the briefing.
- Gives the advisor too many simultaneous decisions before a single client conversation is formed.
- Exposes implementation residue, such as internal workflow terms, artifact lists, and run history, too close to the main path.
- Encourages a dashboard habit: scan everything, then decide what matters.

The advisor workflow should do the reverse: make one guided decision, preserve it, then reveal only the next needed choice.

## Why One-Screen Completeness Is Wrong

Satisfying every visible requirement on one screen is the wrong implementation for Arangur because the product is about communication, not inventory.

A one-screen console can prove capability, but it does not guide judgment. It asks the advisor to interpret the tool before the tool has helped structure the conversation.

The better implementation should:

- Pace decisions in sequence.
- Keep each step visually sparse.
- Use compact summaries to preserve prior choices.
- Reveal evidence only after the briefing frame exists.
- Move technical and artifact material into later appendices.

## Guided Builder Principle

The builder should follow one principle:

```text
One clear choice at a time.
```

Each step should ask for one decision, explain why it matters in plain language, and then carry that choice forward in a compact summary. The advisor should always know where they are in the briefing composition process.

## Target Sequence

1. Choose client question.
2. Choose audience depth.
3. Choose portfolio/source context.
4. Review suggested briefing bundle.
5. Add/remove supporting briefing cards.
6. Review advisor draft.
7. Open client briefing.

The sequence can remain dependency-free and backend-served in the near term. The correction is about product pacing, not framework choice.

## Choice Preservation

Selected choices should not disappear when the advisor moves to the next step. They should collapse into a compact summary such as:

```text
Question: What could hurt us?
Audience: Standard Family Office Meeting
Context: Demo portfolio
Bundle: Scenario impact, largest contributors, concentration context, confidence note
```

The summary should be visible but quiet. It should reassure the advisor that the briefing frame is being built without forcing the previous controls to remain large.

## Initially Visible

The first screen should show only:

- Product name or working title.
- A short sentence explaining that Arangur helps prepare a client briefing from portfolio evidence.
- Synthetic/local demo caveat in compact form.
- The current step label.
- The `Client question` choice.
- A clear continue action.

Recommended first screen shape:

```text
Prepare a client briefing

What is the client asking?
[ Client question selector or choice list ]

Continue
```

## Hidden Until Later

These should not appear on the first screen:

- Audience depth controls.
- Portfolio/source context controls.
- Suggested evidence bundle.
- Report links.
- JSON links.
- Recent run history.
- Technical/demo panels.
- Full caveat blocks.
- Report directory or artifact-browser behavior.

They can appear later when the user reaches the step where they are needed.

## Advisor Notes

Advisor notes should contain material that helps an advisor prepare interpretation but is not automatically client-facing:

- Why this briefing path was suggested.
- Caveat emphasis for the selected client question.
- Proposed follow-up questions.
- Manager-role or concentration interpretation prompts.
- Data limitations written in advisor language.
- Draft language awaiting advisor approval.

Advisor notes are not a raw artifact browser.

## Evidence Appendix

The evidence appendix should contain support for the briefing cards:

- Valuation and cash detail.
- Manager allocation evidence.
- Exposure and overlap tables.
- Scenario impact detail.
- Data confidence summary and review items.
- Links from cards to supporting report sections.

The evidence appendix should be available from the briefing flow but not dominate the first screen.

## Technical/Admin Appendix

The technical/admin appendix should contain implementation and operations material:

- Internal workflow IDs.
- Source adapter names.
- Run IDs.
- Generated artifact paths.
- HTML/Markdown/JSON report links.
- Report package JSON links.
- Local report index links.
- Recent run history.
- Admin/report browser behavior.

This material is still useful. It is simply not the main advisor or client path.

## What Must Be Removed From The Main Console Path

The next UI implementation should remove these from the first-screen/main path:

- Raw report links.
- JSON links.
- Report package links.
- Recent run history.
- Technical details panels.
- Demo mechanics panels.
- Full caveat blocks.
- Report directory and artifact browsing behavior.
- Any primary framing around internal workflows, runs, or artifacts.

These can move to a technical/admin appendix or protected report browser.

## Sparse Guided Builder Acceptance Criteria

A sparse guided builder implementation is acceptable when:

- The first screen has only one primary decision: `Client question`.
- Each subsequent step introduces one new decision.
- Prior choices collapse into a compact summary.
- The builder can suggest a briefing bundle before report artifacts are exposed.
- The advisor can add/remove briefing cards before opening the client briefing.
- The client briefing is a separate surface from the advisor builder.
- Report links and JSON artifacts are absent from the first screen.
- Recent run history is absent from the first screen.
- Technical/admin details are reachable but secondary.
- The synthetic/local caveat remains visible in compact form.
- The implementation still uses synthetic/local data and existing API behavior unless a later backend metadata batch explicitly changes it.
