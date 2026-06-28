# Briefing Set Client Preview Model v1

## Purpose

Client Preview Mode renders the selected report views from a briefing set as a client-facing sequence. It should feel like a meeting-ready briefing assembled from the builder list, not a generic page with static cards.

## Core Behavior

Client Preview Mode should:

- Show selected client-facing report views in order.
- Preserve the narrative flow created in Builder Mode.
- Use concrete portfolio-derived findings where available.
- Hide technical/admin machinery.
- Keep caveats and confidence notes compact and close to the relevant claim.
- Exclude advisor-only notes from the client-facing sequence.

It should not:

- Render one generic briefing page regardless of the selected report list.
- Show workflow IDs, run IDs, artifact paths, raw JSON links, or implementation diagnostics.
- Use generic placeholders when portfolio-derived values or labels are available.
- Treat scenario outputs as forecasts or advice.

## Preview Sequence

Recommended first sequence:

1. Opening answer / meeting frame.
2. Portfolio status.
3. Concentration review.
4. Scenario impact.
5. Verification note.
6. Suggested discussion / follow-up.

The exact sequence should be generated from the ordered report view list. If the advisor removes or reorders views in Builder Mode, Client Preview Mode should reflect that order.

## Client-Facing Tone

The preview should read like an advisor briefing:

- Plain English first.
- Evidence second.
- Caveats where they matter.
- Technical detail in appendices.

Example opening frame:

```text
This briefing reviews whether the demo portfolio is positioned as expected for a quarterly family-office conversation, with a focus on value, cash reserves, concentration, scenario sensitivity, and evidence confidence.
```

## Portfolio-Derived Statements

The preview should replace scaffolding with specific statements when the current report package supports them.

Examples:

- Total portfolio value: "The demo portfolio is valued at approximately the current generated portfolio total as of the report valuation date."
- Cash-like reserves: "Cash-like reserves are visible in the portfolio summary and should anchor the liquidity discussion before concentration or scenario review."
- AI/chip exposure: "The concentration review should call out AI/chip-related exposure when theme tags or scenario mappings identify it."
- Microsoft/NVIDIA overlap: "Where Microsoft or NVIDIA appears across managers or accounts, the overlap should be described as duplicated exposure for review, not automatically as a problem."
- Illustrative scenario impact: "The AI/chip selloff scenario should show the deterministic impact and largest contributors with clear language that it is illustrative, not a forecast."
- Data-confidence/human-review item: "If the data coverage result includes medium/low confidence or human-review items, the preview should state what needs verification before overinterpreting the result."

The wording should use actual available values and labels from the report package whenever possible. If a value is unavailable, the preview should say less rather than invent a conclusion.

## Hidden Technical/Admin Machinery

Client Preview Mode should hide:

- Source adapter controls.
- Workflow type selectors.
- Run history.
- Report package JSON.
- Raw artifact links.
- Local file paths.
- API/debug labels.
- Technical appendix controls unless intentionally opened from an advisor/admin surface.

The technical/admin appendix remains available elsewhere for validation and support, but it should not be part of the client-facing path.

## Preview From Builder State

Client Preview Mode should be derived from:

- Shared briefing context.
- Ordered report view list.
- Visibility status for each view.
- Available report package summaries.
- Confidence and caveat metadata.

It should not be a separately authored static page that drifts away from the builder. The advisor should trust that the preview is the set they just composed.

## Advisor Follow-Up

Suggested discussion/follow-up should translate evidence into questions, not recommendations.

Examples:

- "Which concentrations are intentional?"
- "Which overlapping exposures should be reviewed against manager mandates?"
- "Which data-confidence items should be verified before a decision meeting?"
- "Should the scenario framing be adjusted before sharing with the client?"

This keeps the preview useful for client conversation while avoiding unsupported investment advice.
