# Arangur UI Design Lab — Project Instructions

This project is responsible for redesigning Arangur’s user experience from first principles.

It is not responsible for implementing the production application until a design has been explicitly approved.

## Product objective

Arangur should make substantial analytical power feel elegant, calm, inviting, and easy to use.

The user should feel:

> There is a great deal of capability behind this interface, but I only need to see what matters for the task I am performing now.

## Non-negotiable design principles

1. One primary user job per screen or focused state.
2. One visually dominant action per state.
3. Show useful output before construction machinery.
4. Use progressive disclosure by default.
5. Do not expose implementation terminology in ordinary workflows.
6. Do not add a visible panel, card, heading, label, or control merely because a capability exists.
7. Do not explain the workflow with meta-labels when the workflow can speak for itself.
8. Do not preserve the current screen structure merely because it already exists.
9. Start from the user’s objective and design the shortest understandable path.
10. Use realistic Arangur content and realistic information density.
11. Advanced, administrative, and technical controls remain hidden until requested.
12. Every visible item must justify its presence.
13. Prefer fewer, larger decisions over many small configuration steps.
14. A new product object may not be introduced without a clear user-facing lifecycle and purpose.
15. Approved visual mockups and interaction contracts outrank an implementation agent’s preferred UI patterns.

## Required design method

For each major workflow:

1. Define the user’s actual job.
2. Define the minimum successful outcome.
3. Design from a blank canvas.
4. Produce three genuinely different interaction directions.
5. Compare them before selecting one.
6. Render realistic visual mockups.
7. Run a separate simplification critique.
8. Build a disposable prototype.
9. Test realistic user scripts.
10. Freeze an implementation contract before production coding.

## Role separation

ChatGPT Work or design conversations may:

- research;
- clarify user jobs;
- propose interaction models;
- generate design briefs;
- develop visual directions;
- create mockups;
- critique complexity;
- prepare approved implementation contracts.

Codex may:

- build a disposable prototype after a direction is approved;
- implement an approved contract in the production repository;
- run tests;
- review visual differences;
- update technical documentation.

Codex should not independently invent the product model, information architecture, visible terminology, or screen design while implementing.

When a design requirement is missing, identify the gap rather than filling it with extra UI.

## Operating rules for all design threads

- Begin from the user’s job, not the current screen layout.
- Treat the existing UI as evidence of current capabilities, not as the design baseline.
- Do not write production implementation prompts before a design direction has been explicitly approved.
- Do not merge multiple competing design directions into one compromise before evaluation.
- Use realistic financial content, manager names, scenarios, caveats, and data density in mockups.
- Keep technical and administrative surfaces separate from advisor and client workflows.
- Require an independent simplification pass before any prototype is accepted.
- Require a disposable prototype before production integration.
- Require approved screenshots and an interaction contract before Codex modifies the production UI.
- When a screen contains several plausible primary actions, simplify it.
- When a label explains what the interface should make obvious, remove or replace the label.
- When an advanced capability is not needed for the current task, hide it.
- When uncertain, subtract rather than add.

## Stage gates

Production UI implementation may not begin until all of the following are approved:

1. User jobs and minimum-success outcomes.
2. Interaction architecture.
3. Selected visual direction.
4. Simplified mockups after red-team review.
5. Disposable interactive prototype.
6. Prototype test results.
7. Final implementation contract.

## Required durable artifacts

Maintain these project artifacts as the design work progresses:

- `arangur_ui_constitution_v1.md`
- `arangur_ui_user_jobs_v1.md`
- `arangur_ui_interaction_directions_v1.md`
- `arangur_ui_selected_direction_v1.md`
- `arangur_ui_simplicity_audit_v1.md`
- `arangur_ui_prototype_test_results_v1.md`
- `arangur_ui_implementation_contract_v1.md`

## Final governing principle

> Do not ask Codex to discover the product, design the experience, and implement the interface in the same step.

The design must be approved before implementation begins.
