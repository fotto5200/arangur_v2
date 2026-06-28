# Client Briefing Page Model v1

## Purpose

The client briefing page must be a separate surface from the advisor guided builder.

The builder helps the advisor compose, review, and approve the briefing. The client briefing page presents the approved answer in a clean, answer-first format. These two surfaces can use the same evidence underneath, but they should not expose the same density or mechanics.

## Answer-First Structure

The client briefing page should begin with the answer, not the machinery that produced it.

Recommended top-level structure:

1. Title or family/client name.
2. Client question.
3. Plain-English answer.
4. Three to five key briefing cards.
5. Compact confidence note.
6. Optional buttons for evidence and appendix.

The client should not have to understand workflow IDs, JSON packages, report directories, or implementation status to understand the briefing.

## Page Header

The header should include:

- The title or family name.
- The selected client question.
- A short date or review context when available.
- A compact synthetic/local caveat in demo mode.

Example:

```text
Riverbend Family Review
Question: What could hurt us?
Prepared for: Standard Family Office Meeting
```

## Plain-English Answer

The answer should be concise, advisor-approved, and tied to the selected question.

It should avoid:

- Forecasting certainty.
- Autonomous investment advice.
- Claims that data confidence equals investment quality.
- Overstating what the synthetic demo proves.

## Key Briefing Cards

The client briefing should show three to five cards by default. Cards should be curated by the builder and can vary by question and audience depth.

Examples:

- Portfolio value and cash position.
- Manager allocation.
- Concentration and duplicated exposure.
- Scenario impact.
- Data confidence note.
- Manager role question.

Each card should have:

- A plain-English heading.
- One main takeaway.
- One or two supporting facts.
- Optional link to evidence.

## Compact Confidence Note

The confidence note should be short and close to the answer.

It should summarize whether the briefing is supported by the available synthetic evidence and whether human review is needed. Full data coverage detail belongs in an appendix.

## Optional Appendix Buttons

The client briefing can include compact controls such as:

- `View evidence`
- `View appendix`
- `Advisor notes` when the user is authorized and in advisor mode

These should not look like raw file links.

## Must Not Be Shown By Default

The client briefing page should not show these by default:

- Workflow IDs.
- JSON links.
- Report package links.
- Raw artifact lists.
- Implementation roadmap.
- Full data confidence detail.
- Technical appendix material.
- Run IDs.
- Source adapter names.
- Report directory paths.

These belong in advisor, evidence, or technical layers.

## Layer Model

Arangur should treat the briefing experience as four layers.

### Layer 1: Client Briefing

Purpose: Present the approved answer.

Contains:

- Title/family name.
- Client question.
- Plain-English answer.
- Three to five key briefing cards.
- Compact confidence note.
- Optional evidence/appendix buttons.

Does not contain raw artifacts, workflow IDs, or implementation mechanics.

### Layer 2: Advisor Notes

Purpose: Help the advisor prepare and approve interpretation.

Contains:

- Suggested talking points.
- Caveat emphasis.
- Follow-up questions.
- Unsupported conclusions to avoid.
- Draft language.
- Internal interpretation notes.

This layer can be visible to the advisor before publishing or opening the client briefing.

### Layer 3: Evidence Appendix

Purpose: Show the evidence supporting the briefing cards.

Contains:

- Valuation/cash details.
- Exposure and overlap details.
- Scenario impact details.
- Data confidence summary.
- Human-review items.
- Relevant report sections.

This layer can be client-visible when appropriate, but it should remain organized around evidence, not raw files.

### Layer 4: Technical/Admin Appendix

Purpose: Support implementation review, debugging, operations, and private-demo administration.

Contains:

- Workflow IDs.
- Source adapters.
- Run IDs.
- Artifact paths.
- HTML/Markdown/JSON file links.
- Report package JSON.
- Local report index.
- Recent run history.
- Persistence/admin status.

This layer should be protected or clearly marked as advisor/admin-only. It is not the client briefing and not the first step of the advisor builder.

## Relationship To The Guided Builder

The guided builder should produce or open a client briefing page after the advisor has reviewed the suggested bundle and draft.

The builder asks:

```text
What briefing are we preparing?
```

The client briefing page answers:

```text
Here is the approved answer and the evidence needed for this conversation.
```
