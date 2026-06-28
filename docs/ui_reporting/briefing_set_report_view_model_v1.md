# Briefing Set Report View Model v1

## Purpose

Report views are the building blocks of a briefing set. They are not full reports by default. In the builder, a report view should appear as a compact row or card that can be opened, duplicated, adjusted, moved, or removed.

## Report View Definition

A report view is a configured presentation of portfolio evidence for one part of the client conversation.

Minimum fields:

| Field | Meaning |
| --- | --- |
| Report title | Short client-readable or advisor-readable name. |
| Client question or purpose | The reason this view belongs in the set. |
| Grouping lens | The main grouping dimension, such as manager, theme, sector/industry, holding, or data issue. |
| Focus metric | The primary metric, such as value, cash, exposure, scenario impact, or confidence. |
| Scenario | Optional scenario context, when the view depends on scenario assumptions. |
| Visibility status | Client-facing or advisor-only. |
| Confidence badge | Compact confidence state for the evidence behind the view. |
| Controls | Open, duplicate, change lens, change metric, move, remove. |

## Initial Report View Types

The first implementation should support these report view types:

1. Portfolio status.
2. Concentration review.
3. Scenario impact.
4. Verification / data-confidence note.
5. Advisor follow-up notes.

These are intentionally broad enough to cover the first demo paths without creating a large report taxonomy.

## Initial Lenses

Supported initial grouping lenses:

- Manager.
- Theme.
- Sector/industry.
- Holding.
- Data issue.

The lens determines how the view organizes evidence. For example, "Portfolio status" grouped by manager answers a different meeting need than "Portfolio status" grouped by theme, even when both use the same portfolio source.

## Initial Metrics

Supported initial focus metrics:

- Value.
- Cash.
- Exposure.
- Scenario impact.
- Confidence.

The metric determines what the view emphasizes. For example, a concentration review by theme may focus on exposure, while a verification note by data issue should focus on confidence.

## Compact Builder Representation

The builder should show compact report rows/cards, not full report contents.

A row/card should include:

- Title.
- Purpose line.
- Lens.
- Metric.
- Scenario label, if applicable.
- Visibility state.
- Confidence badge.
- Small controls.

Example compact row:

```text
Portfolio status
Purpose: Open the quarterly review with current value and liquidity.
Lens: manager | Metric: value + cash | Scenario: none | Client-facing | Confidence: medium
[Open] [Duplicate] [Lens] [Metric] [Move] [Remove]
```

The full contents should appear only when the advisor opens a view or enters Client Preview Mode.

## Controls

Open:
Shows view detail without changing the set.

Duplicate:
Creates a new view from the current one so the advisor can vary one axis while preserving the rest of the setup.

Change lens:
Switches the grouping lens while preserving shared context and the view's purpose when possible.

Change metric:
Switches the focus metric while preserving lens and purpose when possible.

Move:
Changes the view's order in the briefing sequence.

Remove:
Drops the view from the set without deleting underlying analytics or artifacts.

## Visibility States

Client-facing views appear in Client Preview Mode.

Advisor-only views remain in the builder or advisor notes area. They can support preparation, caveats, or follow-up tasks without being shown as part of the client-facing sequence.

## Design Constraints

- Do not expose workflow IDs, raw artifact paths, JSON links, or run history in report rows.
- Do not expand every view by default.
- Do not make every possible lens/metric combination a separate top-level workflow.
- Do keep each view understandable as one conversational unit.
