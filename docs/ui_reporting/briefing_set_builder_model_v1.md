# Briefing Set Builder Model v1

## Purpose

The next Arangur browser experience should be a Briefing Set Builder. The recent sparse guided builder is the right correction for focus and progressive disclosure, but it still suggests a one-question / one-report wizard. A real advisor meeting is usually a composed sequence: one shared context, several related views, a client-ready preview, and a saved presentation set that can be revisited.

## Core Correction

The target product is not:

- A dense reporting console.
- A raw artifact browser.
- A one-report guided wizard.
- A page of static briefing cards.

The target product is:

```text
shared briefing context
  + ordered list of report views
  + client-facing preview
  + saved presentation set
```

A briefing set helps the advisor define the meeting frame once, then compose a lightweight sequence of report views that together answer the client conversation.

## Briefing Set Definition

A briefing set is the working unit for an advisor preparing a client conversation.

Minimum model:

- Shared context: the assumptions and defaults that apply across the whole meeting.
- Ordered report view list: compact report rows/cards selected for the conversation.
- Client preview: a client-facing sequence rendered from the selected report views.
- Saved presentation set: the future persisted object that can be reopened, revised, exported, or shared.

Example:

```text
Shared context
- Client/family: Northstar Family Office
- Meeting purpose: quarterly review
- Audience: Standard Family Office Meeting
- Portfolio source: demo portfolio
- Base question: Are we on track?
- Scenario context: AI/chip selloff
- Default lens: manager
- Default metric: value + cash

Generated report views
1. Portfolio status - grouped by manager - value + cash
2. Concentration review - grouped by theme - exposure
3. Scenario impact - AI/chip selloff - P&L impact
4. Verification note - grouped by data issue - confidence
5. Advisor follow-up - advisor-only notes
```

## Shared Context

The advisor should define shared assumptions once because repeated setup creates friction and encourages inconsistent report framing.

Shared context should include:

- Client/family.
- Meeting purpose.
- Audience depth.
- Portfolio source or context.
- Primary client question.
- Scenario context, when relevant.
- Default grouping lens.
- Default focus metric.

The builder can use these values to generate sensible first report views, label them clearly, and keep client-facing language consistent.

## Ordered Report View List

The report list is the main workspace. It should be compact and sequence-oriented, like an agenda of report views rather than a grid of full report outputs.

Each row/card should show enough information to answer:

- What is this view for?
- What lens does it use?
- What metric does it focus on?
- Is it client-facing or advisor-only?
- Is confidence high enough for the intended conversation?

The advisor should be able to open a view for more detail, duplicate it, change one axis, reorder it, or remove it. The default state should remain lightweight.

## Builder Mode And Client Preview Mode

Builder Mode is for preparing the set:

- Define shared context.
- Generate a suggested report list.
- Adjust the sequence.
- Vary lenses, metrics, scenarios, questions, or audience treatment.
- Keep technical/admin material out of the main path.

Client Preview Mode is for rehearsing or showing the client-facing sequence:

- Render selected report views in order.
- Use client-ready language.
- Hide workflow IDs, raw JSON, artifact paths, and implementation diagnostics.
- Show confidence and caveats compactly where they matter.
- Preserve advisor-only notes outside the client-facing flow.

## Work Loop

The builder should support a simple loop:

```text
build -> preview -> adjust -> preview -> save
```

This loop matters because briefing composition is iterative. Advisors often discover that the third view should come second, that a concentration view should be grouped by theme instead of manager, or that a scenario view belongs after the baseline portfolio status.

## Axes Of Variation

Report views should vary one or two axes at a time. This keeps the set understandable and prevents the UI from becoming a combinatorial report generator.

Primary axes:

- Grouping lens: manager, theme, sector/industry, holding, data issue.
- Metric: value, cash, exposure, scenario impact, confidence.
- Scenario: selected scenario or no scenario.
- Client question: the conversation purpose the view supports.
- Audience treatment: client-facing, analytical, advisor-only, or appendix-level.

The key product behavior is controlled variation. If the advisor duplicates "Portfolio status" and changes the lens from manager to theme, that should feel like a small purposeful edit, not a new report workflow.

## Difference From A Reporting Console

A reporting console starts from internal controls, workflows, artifacts, and outputs. It is useful for validation, support, and admin review, but it is not the main advisor experience.

A Briefing Set Builder starts from the client conversation:

- What meeting are we preparing for?
- What question are we answering?
- What sequence of views tells the story?
- What should the client see?
- What should remain advisor-only or technical?

The reporting console remains an appendix/admin surface.

## Difference From A One-Report Guided Builder

A one-report guided builder narrows the problem, but it still makes the advisor pick one question and produce one primary report. That is too small for family-office review work.

A Briefing Set Builder lets the advisor prepare a conversation:

- One shared setup.
- Multiple related views.
- Ordered narrative flow.
- Client preview.
- Future saved set.

This keeps the sparse, guided feeling while matching how advisors actually assemble meeting material.

## Client Conversation Support

The set should feel like an advisor-authored meeting flow:

1. Establish the meeting frame.
2. Answer the primary question.
3. Show the supporting portfolio status.
4. Review concentration or overlap.
5. Test the scenario or concern.
6. State confidence and verification limits.
7. Capture follow-up or advisor-only notes.

Arangur should help the advisor compose that flow from real portfolio-derived findings where available, while keeping caveats visible and avoiding investment advice claims.
