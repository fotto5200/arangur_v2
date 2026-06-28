# Briefing Set Builder Implementation Brief v1

## Purpose

This brief defines the next UI implementation batch. The sparse guided builder should be transformed into a Briefing Set Builder: shared context first, compact ordered report views second, client preview third, and technical/admin material outside the main path.

## Top-Level Modes

Builder Mode:

- Advisor-facing preparation workspace.
- Defines shared context once.
- Generates and edits an ordered report list.
- Shows compact report rows/cards by default.
- Provides controls for open, duplicate, change lens, change metric, reorder, and remove.

Client Preview Mode:

- Client-facing rendering of selected report views in order.
- Uses concrete portfolio-derived findings where available.
- Hides technical/admin machinery.
- Shows confidence/caveats in concise client-appropriate language.

## Shared Context Setup

The first implementation should let the advisor define:

- Client/family.
- Meeting purpose.
- Audience depth.
- Portfolio source/context.
- Primary client question.
- Scenario context.
- Default grouping lens.
- Default focus metric.

The UI should present this as one concise setup area, not repeated controls on every report.

## Report Set Generation

After shared context is defined, the UI should generate a suggested report set.

Initial generated set:

1. Portfolio status.
2. Concentration review.
3. Scenario impact.
4. Verification / data-confidence note.
5. Advisor follow-up notes.

The generated list should inherit the shared context and choose sensible default lenses and metrics. The advisor can then adjust individual views without restarting the whole builder.

## Compact Ordered Report List

The main builder surface should be an ordered list of report rows/cards.

Each row/card should show:

- Report title.
- Client question or purpose.
- Grouping lens.
- Focus metric.
- Scenario, if applicable.
- Client-facing vs advisor-only status.
- Confidence badge.
- Controls.

The builder should not show full report contents by default. Full content belongs behind an open action or in Client Preview Mode.

## Report Row/Card Behavior

Rows/cards should be stable and compact. They should support scanning, reordering, and small edits without visual noise.

Recommended behavior:

- Open: inspect details for one view.
- Duplicate: copy a view so one axis can be changed.
- Change lens: change grouping, such as manager to theme.
- Change metric: change focus, such as value to exposure.
- Reorder: move a view earlier or later in the client sequence.
- Remove: drop the view from the set.

Changing a lens or metric should preserve shared context and avoid creating a new global workflow selection step.

## Client Preview Behavior

Client Preview Mode should render the ordered client-facing views from the builder state.

It should include:

- Opening answer / meeting frame.
- Selected report views in order.
- Concrete portfolio-derived statements when available.
- Compact confidence and caveat notes.
- Suggested discussion or follow-up.

It should exclude:

- Advisor-only views.
- Raw workflow names.
- Run IDs.
- JSON links.
- Artifact paths.
- Technical diagnostics.

## Technical/Admin Appendix Behavior

Technical/admin artifacts remain available outside the main path.

The appendix can expose:

- Source adapters.
- Workflow names.
- Run IDs.
- Report package links.
- HTML/Markdown/JSON artifacts.
- Local report index.
- Recent runs.
- Validation/debug data.

The main builder and client preview should not depend on those details being visible.

## Remove Or Hide From Main Path

Hide or remove from the main builder path:

- Raw report links.
- JSON links.
- Report package links.
- Run history.
- Workflow IDs.
- Source adapter machinery.
- Large caveat blocks.
- Debug labels.
- Repeated explanatory text.
- Headings that restate obvious UI structure.

Keep caveats visible, but place them near the relevant claim or in compact global notes.

## Heading And Visual-Noise Correction

The next UI should reduce headings and repeated instructional copy. The experience should feel like a light advisor workspace, not a documentation page rendered in the browser.

Use concise labels, compact controls, and stable rows/cards. Reserve larger headings for the mode or set name, not every subsection.

## First Implementation Scope

First scope should remain dependency-free unless explicitly changed:

- Update the current static app UI.
- Reuse existing file-backed API responses.
- Derive first report-set content from existing run summaries/report package metadata.
- Keep all data synthetic/mock.
- Keep the technical/admin appendix available.
- Avoid backend schema changes unless a minimal compatibility field is unavoidable.
- Do not implement real save/load persistence until the save/load skeleton batch.

## Acceptance Criteria

1. UI is clearly a briefing-set builder, not a one-report wizard.
2. Advisor defines shared context once.
3. UI generates an ordered report list.
4. Advisor can see report list without seeing full report contents.
5. Advisor can modify a report by varying one axis.
6. Advisor can move between Builder Mode and Client Preview Mode.
7. Client preview shows selected reports in order.
8. Client preview uses concrete portfolio-derived findings, not generic placeholders.
9. Technical/admin artifacts are not visible in the main path.
10. Headings and repeated explanatory text are reduced significantly.
11. Experience feels lightweight, elegant, and advisor-guided.
12. Guided-builder correction docs are updated to state that the target has evolved from one-report guided builder to briefing set builder.
