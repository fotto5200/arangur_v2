# UI Reporting Philosophy v1

## Product Thesis

Arangur is a portfolio communication system. It is not primarily a dashboard, report generator, analytics console, or workflow runner.

The core product gap is the distance between how complex multi-manager portfolios are sold or discussed and how they are later reported. Advisors often explain a portfolio through themes, manager roles, client concerns, cash needs, and risk stories. Later, reporting tools usually return account tables, holdings lists, generic allocation charts, or risk metrics that do not clearly answer the conversation the advisor has actually been having.

Arangur should help an advisor answer:

```text
Given the way I have been talking to this client, what does the current portfolio actually say?
```

The system should be designed from briefing and conversation backward, not from analytics modules forward. Analytics matter because they support the briefing. Reports matter because they preserve the briefing. The product experience should begin with the client question.

## Briefing-Room-First Principle

The first product metaphor should be briefing room or control room, not dashboard.

A dashboard asks, "What metrics do we have?"

A briefing room asks, "What conversation do we need to have, and what evidence supports it?"

The difference should shape the user interface:

- The first visible label should be `Client question`.
- The default audience mode should be `Standard Family Office Meeting`.
- The system should prepare a briefing, not merely run a pipeline.
- Evidence should be presented in support of an answer, not as unorganized tiles.
- Drill-down should exist, but the top layer should remain a narrative structure.

## Advisor Workspace Versus Client Briefing

Arangur should distinguish between an advisor workspace and a client-facing briefing.

The advisor workspace can show:

- Source status and data coverage.
- Workflow execution details.
- Internal caveats and uncertainty.
- Manager overlap diagnostics.
- Missing data and verification needs.
- Links to raw JSON, report packages, and technical outputs.

The client briefing should show:

- The client question.
- A plain-English answer.
- The minimum evidence needed to support the answer.
- Interpretation in the client's language.
- Proposed actions or review questions.
- Confidence and caveats phrased responsibly.

The same underlying run can feed both surfaces, but the presentation should be different.

## AI Role

The product stance should be:

```text
AI proposes. Arangur computes. Advisor approves.
```

AI can propose a briefing frame, draft language, suggest client questions, and summarize evidence. Arangur should compute valuations, exposures, overlap, scenario impacts, and data-confidence signals deterministically where possible. The advisor approves the final interpretation and client-facing language.

This prevents the product from overclaiming. The AI is not the authority. The advisor is not replaced. The analytics are not hidden. The system gives the advisor a better briefing room.

## What The UI Should Avoid

The UI should avoid leading with:

- Workflow names as the primary product metaphor.
- Raw analytics modules as the primary navigation.
- Generic dashboard tiles disconnected from a client question.
- Dense tables before a plain-English answer.
- "Run pipeline" language.
- Source selection as the first decision unless the user is in an internal setup mode.
- Client-facing claims that imply investment advice, forecasting certainty, or production-grade reconciliation.

Workflow and source controls remain useful internally. They should become secondary or behind-the-scenes controls in the main briefing experience.

## Implications For The Current Demo Console

The current browser console is technically useful but philosophically transitional. It proves that the app can:

- List sources and workflows.
- Run the local synthetic pipeline through the API.
- Show run history.
- Link generated artifacts.
- Surface data-confidence context.

The next UI iteration should keep those capabilities but reframe them around:

- `Client question` as the first control.
- Audience depth as the second control.
- Optional source selection as a secondary advisor control.
- Internal workflow mapping behind the scenes.
- A briefing preview and evidence panel instead of a raw run summary.

The console should evolve from "source + workflow + run" to "client question + audience depth + prepare briefing."
