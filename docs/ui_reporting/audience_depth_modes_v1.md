# Audience Depth Modes v1

## Purpose

Audience depth modes control how much detail, caveat language, and drill-down appears in a briefing. The same evidence can be rendered differently for a quick principal conversation, a family office meeting, an analytical review, or an internal advisor workspace.

Frank decision: the default first-demo audience mode should be `Standard Family Office Meeting`.

## Executive / 10-Minute Mode

- Intended user: Principal, client, or decision-maker with limited time.
- Level of detail: Very concise. One answer, three to five evidence points, one proposed next step.
- Visual density: Low. Use short cards and plain-English labels.
- Caveat depth: Essential caveats only, close to the answer.
- Appendix/drill-down behavior: Hidden by default, accessible through "show details" or appendix links.
- Hidden by default: Raw workflow names, JSON links, detailed manager tables, source debug information, and low-level data coverage dimensions.
- Shown by default: Client question, answer, top evidence, confidence label, and advisor-approved action framing.

## Standard Family Office Meeting Mode

- Intended user: Advisor and client/family office group in a normal review meeting.
- Level of detail: Moderate. Enough evidence to support discussion without overwhelming the room.
- Visual density: Medium. Use evidence cards, concise tables, and supporting charts when useful.
- Caveat depth: Visible and specific, especially for scenario assumptions, synthetic data, and data confidence.
- Appendix/drill-down behavior: Available but secondary. The main briefing should stand on its own.
- Hidden by default: Internal API terminology, raw source/workflow controls, full JSON artifacts, and implementation diagnostics.
- Shown by default: Client question, plain-English answer, manager/exposure/scenario evidence, interpretation, proposed action, confidence and caveats.

This is the default first-demo mode.

## Analytical Stakeholder Mode

- Intended user: CIO, analyst, investment committee member, or technically curious client representative.
- Level of detail: High. Shows methodology context, more dimensions, and comparative evidence.
- Visual density: Medium to high. More tables and drill-down panels are acceptable.
- Caveat depth: High. Show assumptions, mapping limits, data coverage, and known missing fields.
- Appendix/drill-down behavior: Prominent. Evidence should connect to report sections and artifacts.
- Hidden by default: Operational implementation details that do not improve analytical review.
- Shown by default: Scenario assumptions, manager/category exposure grids, overlap diagnostics, data confidence dimensions, and artifact links when appropriate.

## Advisor/Internal Mode

- Intended user: Advisor, operations reviewer, product reviewer, or internal implementation user.
- Level of detail: Full. This mode can show the raw mechanics needed to validate, debug, or prepare a client briefing.
- Visual density: High but organized.
- Caveat depth: Full. Include synthetic-data flags, source status, missing inputs, unsupported conclusions, and verification needs.
- Appendix/drill-down behavior: Open and explicit. Raw artifacts and report packages may be visible.
- Hidden by default: Nothing required for internal review, as long as secrets and real client data are never exposed.
- Shown by default: Source adapter, workflow mapping, run ID, artifact links, data coverage details, caveats, and follow-up tasks.

## Design Rule

Audience depth should not change the underlying math. It changes presentation, caveat detail, evidence density, and drill-down defaults.
