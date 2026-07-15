# Advisor Workflow UI Application Architecture v1

Status: recommended for Frank review; not final and not implementation authorization

Canonical product name: **Arangur**. Older `ARRANGER_...` filenames and historical artifacts retain their existing names, but the transcription error is not propagated in new prose.

## Decision to make

Choose the application-level interaction architecture that will carry the four canonical briefing types, reusable definitions, dated generated briefings, advisor review, client presentation, evidence, and history. The design lab leaves Briefing Desk, Arangur Guide, and Investment Library unresolved and forbids an implicit hybrid. Sources: `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_interaction_directions_v1.md` and `docs/project_control/ARRANGER_UI_BLUEPRINT_INPUT_PACKET_v1.md`.

## Evaluation criteria

The architecture must support the six design-lab jobs:

1. Open and present an existing briefing.
2. Reuse a template with current data.
3. Create or modify a reusable template.
4. Review portfolio and manager alignment.
5. Inspect evidence without losing context.
6. Find and reopen an immutable historical briefing.

It must also expose the four committed workflow families in business language, keep one dominant action per state, preserve client/advisor visibility, and avoid raw report-library or execution terminology. Sources: `C:/Users/fotto/cursor/Arangur UI Design Lab/arangur_ui_user_jobs_v1.md`, `docs/product/report_workflow_catalog_v1.md`, and `docs/project_control/ARRANGER_DECISION_REGISTER_v1.md`.

## Option 1: Briefing Desk

### Core idea

The dated generated briefing is the center of gravity. Reading, presentation, contextual evidence, history, and current-data recreation begin from a document context.

### Serves well

- Open/present an existing briefing.
- Inspect claim-bound evidence and return to the same place.
- Reopen immutable historical briefings.
- Keep presentation calm and free of authoring controls.

### Serves poorly

- A first-time advisor who knows the meeting goal but not the object to open.
- Portfolio/manager oversight, which is not naturally a document.
- Discovering which of the four canonical briefing types to prepare.
- Template maintenance when document layout dominates intent.

### Risks

- The document becomes a dumping ground for every analysis.
- Alignment feels secondary.
- A destination switcher grows into conventional navigation.

### Carry forward

- Immutable document identity and fixed dates.
- Reader/presentation separation.
- Evidence anchored to a claim.
- Exact return to reading position.

### Reject or defer

- Opening directly into the last document as the universal first screen.
- Treating every oversight job as a briefing document.

## Option 2: Arangur Guide

### Core idea

The user states an objective in business language; the guide asks only consequential questions and returns a focused output.

### Serves well

- Users who know the outcome but not the object or template.
- Ambiguous historical searches.
- Cross-domain questions linking an alignment concern to a client briefing.
- Keeping platform structure out of view.

### Serves poorly

- Stable spatial overview of ordered sections.
- Predictable template authoring and maintenance.
- High-trust deterministic selection when the guide could infer the wrong client, template, or date.
- Fast repeat use by users who already know the canonical briefing type.

### Risks

- Conversation clutter and repeated clarification.
- Opaque interpretation and discoverability.
- A generative control surface may weaken trust in fixed outputs.

### Carry forward

- Business-job framing.
- Ask only consequential questions.
- Answer first in alignment review.
- A small number of recognizable starting requests.

### Reject or defer

- Free-form conversation as the primary v1 application shell.
- Assistant-selected template/client without explicit confirmation.
- Visible agent reasoning or system narration.

## Option 3: Investment Library

### Core idea

Users locate durable Briefings, Templates, or Portfolios, then enter a focused object lifecycle. Alignment is a view of a portfolio; evidence belongs to a claim.

### Serves well

- Retrieval of known objects and historical briefings.
- Clear template versus generated-briefing distinction.
- Ownership, approval, and future retention metadata.
- A stable portfolio home for alignment review.

### Serves poorly

- Advisors who begin from a meeting goal rather than an object.
- Cross-object work such as turning an oversight finding into a briefing.
- Immediate value when the user must navigate collections first.

### Risks

- A dense filing system or dashboard.
- Metadata crowds out content.
- Every backend object becomes a visible collection.
- Search grows into technical filtering.

### Carry forward

- Explicit object lifecycles.
- Immutable historical retrieval.
- Evidence is not an independent library.
- Alignment belongs to the managed portfolio context.

### Reject or defer

- Library/collection navigation as the default first screen.
- Mixed dashboards, activity feeds, and independent evidence collections.

## Recommended named architecture: Conversation Briefing Desk

### Recommendation status

**Recommended for Frank review. Not final until Frank approves it.**

### Core idea

Arangur begins with the advisor's business conversation and ends in a trusted dated briefing. The first screen asks **“What conversation are you preparing?”** and presents the four canonical **Briefing types**. After selection, the advisor enters a focused template/configuration and review path. Once generated, the dated briefing becomes the center of reading, client preview, presentation, evidence, and historical reopening.

This is a named, bounded composite—not an implicit blend:

- From **Arangur Guide**, it borrows only business-job framing and consequential questions. It does not adopt free-form conversation as the v1 shell.
- From **Briefing Desk**, it adopts the dated document as the center of gravity after generation, including presentation and claim-bound evidence.
- From **Investment Library**, it borrows only explicit template/briefing lifecycles and secondary historical retrieval. It does not adopt collection navigation as the first screen.

### Why a pure option fails

- Pure Briefing Desk does not adequately serve the required job/conversation-led first screen or first-time briefing preparation.
- Pure Guide introduces interpretation and trust risk before the deterministic four-workflow path is settled.
- Pure Investment Library starts from objects and retrieval when the accepted product thesis starts from the client conversation.

### Job-to-behavior map

| User job | Architecture behavior |
| --- | --- |
| Present existing briefing | Open from Recent briefings or history; dated briefing reader leads to Presentation. |
| Generate with current data | Choose a Briefing type or reusable template; confirm consequential context; create a new briefing. |
| Maintain reusable template | Duplicate an approved built-in, adjust bounded fields, preview, and save as a custom template. |
| Review alignment | Choose Advisor / Manager Oversight; enter exception-first Advisor Review, not a client document. |
| Inspect evidence | Open Explain or Verify from the exact claim; return to the same claim and position. |
| Reopen history | Use secondary Prior briefings search/list; open the immutable dated briefing. |

### First-screen shape

- Heading: **Prepare a briefing**.
- Question: **What conversation are you preparing?**
- Choice group label: **Briefing types**.
- Four choices:
  - Principal / Family Office Briefing
  - Engaged Client / Investment Committee Review
  - Advisor / Manager Oversight
  - External Manager Story Translation
- Dominant action after a choice: **Continue**.
- Secondary path: **Open a prior briefing**.
- Template maintenance is subordinate: **Manage templates**.
- Developer / QA is separately entered and never a peer primary action.

### Carry-forward elements

- Business-language choice before report inventory.
- Approved built-ins as stable starting points.
- Bounded duplication/editing rather than unconstrained construction.
- Separate Advisor Review, Client Preview, and Presentation.
- Dated immutable briefing reader after generation.
- Claim-bound Explain and Verify.
- Secondary history/retrieval.

### Rejected or deferred elements

- Free-form AI guide as the v1 entry.
- Object-library dashboard as the first screen.
- Opening the last briefing automatically for every user.
- A mixed dashboard of briefings, templates, portfolios, tasks, and analytics.
- Independent evidence library.
- Production-grade durable history in the UI wiring tranche.
- Silent hybridization beyond the behaviors named above.

## Approval gate

Frank must approve or revise:

1. The Conversation Briefing Desk name and center of gravity.
2. The first-screen question and `Briefing types` label.
3. The secondary placement of prior briefings and template management.
4. The deferral of a free-form Guide and library-first shell.

No advisor-facing UI wiring should begin until this architecture decision is recorded as approved in project control.
