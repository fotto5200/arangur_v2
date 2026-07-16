# Arangur Advisor Workbench Information Architecture v1

Status: implemented local product contract
Date: 2026-07-16
Product: Arangur

## Decision

The ordinary advisor home is the Arangur Advisor Workbench. It organizes the product around four activities rather than four illustrative workflows:

1. **Prepare a New Briefing Plan**
2. **Work with Existing Plans or Briefings**
3. **Present a Dated Briefing**
4. **Ask Arangur**

The four existing workflow families remain important examples, but they are now **Arangur example Briefing Plan Templates** inside the template library. They do not define the full universe of supported advisor work.

The governing sequence is: stabilize application structure first; redesign populated Briefing Section reading and visuals in a later tranche.

## Canonical vocabulary

| Term | Meaning | Status/actions |
| --- | --- | --- |
| **Briefing Plan** | Selected Briefing Sections, parameters, order, audience, and visibility rules. | Revise, duplicate, or create a Dated Briefing. |
| **Briefing Plan Draft** | An unfinished Briefing Plan. | Continue at its exact builder stage. |
| **Briefing Plan Template** | A reusable Briefing Plan supplied by Arangur or created by an advisor. | Use as is or customize. |
| **Dated Briefing** | Populated output created by applying data to a Briefing Plan as of a stated date. | View, compare, preview, or present according to status. |
| **Briefing Section** | One populated component inside a Dated Briefing. | Read, Explain, Verify, Previous, or Next. |

The core relationship is:

> **Briefing Plan + Current Data = Dated Briefing**

“Briefing” alone is avoided where the distinction matters. “Report” is not introduced as the ordinary noun for a Briefing Section. Historical code, API payloads, schemas, filenames, and browser-storage keys retain compatibility-oriented internal terms.

## Top-level menu and navigation targets

| Primary activity | Navigation target | Meaning |
| --- | --- | --- |
| Prepare a New Briefing Plan | `#prepare` | Start from scratch, a template, a prior plan, or a draft. |
| Work with Existing Plans or Briefings | `#existing` | Revise plans; create, compare, or view Dated Briefings. |
| Present a Dated Briefing | `#present-hub` | Open, preview, present, resume, or find reviewed material. |
| Ask Arangur | `#ask-arangur` | Deterministic product guidance and routing. |

Hash names are implementation details and are not displayed in ordinary UI.

## Prepare a New Briefing Plan

### Build a new briefing plan

Target: `#new-plan-setup`.

The setup asks only for intended audience, purpose/main question, and desired detail. Audience includes **Advisor/internal**, **Client**, and **Manager discussion**. **Choose briefing sections** opens the restored staged builder at the Briefing Sections stage. Purpose, audience, and detail are prefilled.

The full builder remains available: Purpose; Briefing Sections; Configure; Order & visibility; Preview. Supported catalog choices, parameters, narrative sections, add/remove/reorder/duplicate, visibility, gating, and governance remain unchanged.

### Start from a briefing plan template

Target: `#template-library`.

The library separates:

- Arangur example templates;
- advisor-created templates.

Each row shows audience, purpose, included Briefing Sections, and approximate detail. **Customize** is at least as prominent as **Use as is**.

The four Arangur examples are:

- Principal / Family Office Briefing;
- Engaged Client / Investment Committee Review;
- Advisor / Manager Oversight;
- External Manager Story Translation.

### Start from a prior briefing plan

Target: `#prior-plans`.

The list shows saved plans and recoverable plan meaning from earlier Dated Briefings. It includes plan name, audience, last use, section summary, and prior Dated Briefing count. Actions are **Use the same plan** and **Revise the plan first**.

### Continue an unfinished briefing plan draft

Target: `#drafts`.

Browser-local drafts store the exact builder stage plus name, audience, last edited time, and remaining stages. Every shortcut to a draft uses the same **Continue plan** behavior.

## Work with Existing Plans or Briefings

Second-level order is binding:

1. **Revise or continue a briefing plan** (`#plan-list`) combines Briefing Plan Drafts and saved Briefing Plans. Drafts continue; saved plans revise directly or create a copy.
2. **Create a dated briefing with current data** (`#create-dated`) selects a Briefing Plan, confirms current saved metadata and unavailable material, creates a new immutable Dated Briefing, preserves the plan/history, and opens the first populated Briefing Section in Advisor Review.
3. **Compare dated briefings** (`#compare`) compares stored dates, source plans, section sequences, and saved configuration where present. It does not infer unrecorded values or complete historical positions.
4. **View a dated briefing** (`#dated-list`) opens the first populated Briefing Section, not section definitions or setup metadata.

## Present a Dated Briefing

| Choice | Target | Dominant action |
| --- | --- | --- |
| Open a briefing ready to present | `#ready-list` | Open briefing |
| Preview what the audience will see | `#audience-preview-list` | Start preview |
| Launch a presentation | `#launch-list` | Present briefing |
| Resume a recent presentation | `#resume-list` | Resume presentation |
| Find a briefing | `#find-briefing` | Open selected briefing |

Ready means Advisor Review is complete. Client Preview preserves the exact audience-visible sequence and caveats. Presentation retains clean chrome, Previous/Next, Explain/Verify, and immutable content. Browser-local Dated Briefings add compatible `review_status`, `reviewed_at`, `last_previewed_at`, `last_presented_at`, and `presentation_position` fields.

## Ask Arangur scope

Ask Arangur is deterministic local guided assistance, not a live AI-analysis service. It provides:

- help deciding where to start;
- search/routing to a Briefing Plan or Dated Briefing;
- Briefing Plan preparation guidance;
- an updated-briefing route using a prior plan;
- concise product-term explanations and contextual Explain/Verify routing;
- meeting-preparation questions;
- ordinary product-problem guidance and technical escalation.

It does not fabricate data or Briefing Sections, make investment recommendations, silently perform destructive changes, bypass governance, or claim an external AI connection. Its choices route into the same underlying application states used elsewhere, allowing a future assistant implementation to enhance the interface without changing the object model.

## Shared shortcuts

The home places three secondary shortcuts below the four primary activities:

- **Recent Work** — a mixed, time-ordered list with explicit labels: Briefing Plan Draft, Saved Plan, Dated Briefing, or Ready to Present.
- **Ready to Present** — reviewed Dated Briefings with Preview and Present actions.
- **Recent Dated Briefings** — recently created populated Dated Briefings with View briefing.

The same underlying record and action wording are used when an item appears in more than one shortcut.

## Object and status behavior

| Object/status | Available ordinary actions |
| --- | --- |
| Briefing Plan Draft | Continue plan |
| Saved Briefing Plan | Open/revise, create a copy, or create a Dated Briefing |
| Dated Briefing — in review | View populated Briefing Sections, Explain/Verify, complete review |
| Ready Dated Briefing | View, compare, preview, or present |

Status determines actions. The advisor is not required to infer technical completeness rules.

## Developer / QA boundary

Developer / QA remains a small footer entry and separate route. It may show internal IDs, storage keys, schemas, JSON transfer, source/fixture paths, migration state, gate reason codes, and validation diagnostics. None of that competes with the four primary activities or appears in Client Preview/Presentation.

## Compatibility and legacy records

Existing keys remain in use:

- `arangur.local_named_briefing_workflows.v1` for reusable saved definitions;
- `arangur.local_briefings.v1` for immutable Dated Briefings;
- `arangur.local_generated_reports.v1` for earlier generated-report shelf compatibility.

A new compatible key, `arangur.local_briefing_plan_drafts.v1`, stores unfinished builder state.

Records with recognizable client/advisor set meaning are normalized at runtime and remain usable. Records without a reliably recognizable current plan shape are classified `legacy_incompatible`, retained in storage, hidden from ordinary current lists, and disclosed through Developer / QA. Earlier generated-report shelf records are likewise retained as Legacy and excluded from ordinary Dated Briefing lists. No user-created record is silently deleted.

## Preserved lifecycle and capability

The implementation preserves built-in examples, from-scratch and deep customization, the approved Briefing Section catalog, supported parameters, reusable custom plans, immutable Dated Briefing creation, Advisor Review, Client Preview, Presentation, Explain/Verify with exact return, history, external-story governance, honest gating, browser-local persistence, legacy normalization, and Developer / QA.

## Deferred Dated Briefing reader and visual redesign

This tranche changes navigation into the reader so actual populated Briefing Sections are the apparent Dated Briefing. It does not redesign the populated Briefing Section visuals, import HTML prototypes, change analytics, or create new output math.

The planned next visual tranche is:

**Arangur Dated Briefing Reader and Design-Lab Visual Integration v1**
