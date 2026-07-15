# Advisor Workflow UI State Map v1

Status: implementation-oriented product contract for Frank review; no UI implementation authorized

Architecture assumption: **Conversation Briefing Desk**, recommended but not final. If Frank selects another architecture, this map must be revised before wiring.

## Global state rules

- One primary user job and one visually dominant action per focused state.
- Prior choices collapse into a quiet summary; their full controls do not remain open.
- Business language is visible; internal workflow/report/artifact machinery is hidden.
- Advisor Review, Client Preview, Presentation, and Historical Reading are distinct state intents even when they share rendering components.
- Explain and Verify preserve exact return to the originating claim.
- Developer / QA is separately entered.

## State 1: Home / Conversation Chooser

| Field | Contract |
| --- | --- |
| User job | Start the right advisor/client conversation or reopen a prior briefing. |
| Dominant action | **Continue** after selecting one Briefing type. |
| Secondary actions | Open a prior briefing; Manage templates. |
| Visible content | “Prepare a briefing”; “What conversation are you preparing?”; four canonical Briefing types; short audience/purpose descriptions; compact synthetic-data notice in the demo. |
| Hidden content | Report catalog, generated artifacts list as a peer section, template internals, run history, API/JSON, Developer / QA controls. |
| Inputs | Selected briefing type. |
| Outputs | Internal workflow ID and approved built-in template selection. |
| Transitions | Continue → Template Selection/Configure; Prior briefing → Historical Items; Manage templates → Template Selection. |
| Acceptance criteria | All four types are present in business language; one selection is required; no raw report/library machinery appears above the fold. |
| Common failure mode | Recreating the current home as equal-weight Templates, Generated Reports, creation, and QA sections. |

## State 2: Template Selection / Reuse

| Field | Contract |
| --- | --- |
| User job | Choose the approved reusable definition for the selected conversation. |
| Dominant action | **Use template**. |
| Secondary actions | Preview sections; Duplicate template; Back. |
| Visible content | Template name, purpose, audience, ordered section summary, owner/approval when material, last use, fixed caveats. |
| Hidden content | Prompt/schema/model settings, source bindings, renderer controls, raw workflow ID, edit controls when reuse intent is active. |
| Inputs | Briefing type, chosen built-in/custom template. |
| Outputs | Template identity and version for configuration. |
| Transitions | Use → Configure; Duplicate → Builder; Back → Home. |
| Acceptance criteria | Reuse and maintenance intents do not share equal-weight action bars; built-ins are visibly approved/read-only. |
| Common failure mode | Turning the state into a filter-heavy Investment Library or exposing every template metadata field. |

## State 3: Builder / Template Configure

| Field | Contract |
| --- | --- |
| User job | Create a bounded custom template by modifying an approved starting point. |
| Dominant action | **Preview template**. |
| Secondary actions | Reorder; include/exclude; change visibility; edit caveat; discard. |
| Visible content | Name, audience, purpose, compact ordered sections, client/advisor visibility, optional/gated state, plain-language emphasis/exclusions, unsaved state. |
| Hidden content | Universal report combinatorics, schemas, raw IDs, source/view paths, model settings, construction primitives, production permissions. |
| Inputs | Duplicate of built-in or existing custom template; bounded editable fields. |
| Outputs | Draft template definition. |
| Transitions | Preview → Template Preview; Discard → Template Selection. |
| Acceptance criteria | Built-in source cannot be overwritten; no from-scratch blank report console in the default path; external-story governance fields cannot be removed. |
| Common failure mode | Preserving the current full report-element finder as the primary template-authoring experience. |

## State 4: Template Preview / Save

| Field | Contract |
| --- | --- |
| User job | Confirm that a reusable definition produces the intended ordered conversation without generating a live briefing. |
| Dominant action | **Save template**. |
| Secondary actions | Back to edit; Cancel. |
| Visible content | Representative section outline, audience/purpose, visibility summary, changed elements, explicit preview-data label. |
| Hidden content | Generation action as a peer, technical diff, renderer controls, internal identifiers. |
| Inputs | Draft template and representative synthetic content. |
| Outputs | Saved custom template. |
| Transitions | Save → Template Selection or Configure; Back → Builder. |
| Acceptance criteria | Preview is unmistakably not a dated client briefing; changes are summarized. |
| Common failure mode | Saving a preview as if it were a generated historical briefing. |

## State 5: Briefing Configuration / Readiness Confirmation

| Field | Contract |
| --- | --- |
| User job | Confirm only the consequential inputs required to create one briefing. |
| Dominant action | **Create briefing with current data**. |
| Secondary actions | Back; change template. |
| Visible content | Client/portfolio, audience, proposed data-as-of date, template, material readiness/caveat summary, what will be client-visible. |
| Hidden content | Section micro-settings, data connectors, run/pipeline controls, model choice, source inventory, detailed diagnostics. |
| Inputs | Template, portfolio/client, audience, current data date/readiness. |
| Outputs | New immutable dated briefing artifact. |
| Transitions | Create → Advisor Review; Back → Template Selection/Builder. |
| Acceptance criteria | Current-data action is explicitly generative; no existing historical briefing is mutated; missing prerequisites block only affected outputs. |
| Common failure mode | “Populate workflow” language or a settings form that exposes operational machinery. |

## State 6: Advisor Review

| Field | Contract |
| --- | --- |
| User job | Decide what is accurate, sufficiently supported, and appropriate for the intended audience. |
| Dominant action | **Preview for client** for client workflows; **Complete review** for advisor-only workflows. |
| Secondary actions | Open evidence; include/exclude optional step; return to template; create revised briefing when changes require regeneration. |
| Visible content | Dated briefing identity; ordered journey; client-facing and advisor-only markers; material caveats; gated reasons; optional steps; internal notes; evidence access. |
| Hidden content | Raw paths/IDs, unrelated diagnostics, model/run internals, template construction controls inside the content. |
| Inputs | Generated briefing plus visibility/gate metadata. |
| Outputs | Approved client-visible sequence or completed advisor-only review. |
| Transitions | Preview → Client Preview; Evidence → Explain/Verify; Complete → Historical Reading; revise → configuration/new briefing. |
| Acceptance criteria | Advisor-only/setup/internal-control material cannot leak into client preview; visibility changes are explicit and auditable in the artifact model. |
| Common failure mode | Treating advisor review as the same rendering and controls as client preview. |

## State 7: Client Preview

| Field | Contract |
| --- | --- |
| User job | Rehearse exactly what the client will see and verify narrative order. |
| Dominant action | **Present**. |
| Secondary actions | Back to Advisor Review; open contextual Explain/Verify as the advisor. |
| Visible content | Exact client-visible sequence, conclusions, material caveats, dates, progress, client-readable evidence paths. |
| Hidden content | Advisor-only/setup/diagnostic/internal-control steps, visibility controls, authoring, generation, export/admin, raw artifact references. |
| Inputs | Advisor-approved client sequence. |
| Outputs | No new object; exact presentation rendering contract. |
| Transitions | Present → Presentation; Back → Advisor Review; Explain/Verify → Evidence. |
| Acceptance criteria | Content and order equal Presentation; only chrome differs; hidden steps cannot be reached through client navigation. |
| Common failure mode | A generic static preview that ignores the selected ordered journey. |

## State 8: Presentation

| Field | Contract |
| --- | --- |
| User job | Deliver a clear client/committee conversation without construction or administration. |
| Dominant action | **Next**. |
| Secondary actions | Previous; Explain; Verify/Evidence; Exit. |
| Visible content | One conclusion/current section, no more than the information budget allows, as-of date, discreet progress, material caveat, exit. |
| Hidden content | Editing, generation, template, source selection, export, admin, report library, Developer / QA, advisor-only notes. |
| Inputs | Approved briefing and current presentation position. |
| Outputs | No content mutation; updated reading position only. |
| Transitions | Next/Previous within journey; Evidence → Explain/Verify; Exit → exact Client Preview/Reader position. |
| Acceptance criteria | One dominant Next action; fixed dates; presentation cannot change the briefing; reduced-motion/static behavior remains meaningful. |
| Common failure mode | Control-heavy reader or full table as the opening explanation. |

## State 9: Explain / Verify / Evidence

| Field | Contract |
| --- | --- |
| User job | Understand or verify one visible claim without losing context. |
| Dominant action | **Back to conclusion** at Verify depth; **Verify** at Explain depth. |
| Secondary actions | Open named source/analysis where authorized. |
| Visible content | Originating claim; concise causal/composition explanation; exact values, basis, period, data date, named sources, assumptions, contradictory evidence, material caveat; exact table when reconciliation is the job. |
| Hidden content | Unrelated evidence, raw provenance infrastructure, chain of thought, query/pipeline/debug data, broad source inventory. |
| Inputs | Claim ID, briefing ID/date, originating state and position. |
| Outputs | No change to briefing; preserved return token/position. |
| Transitions | Explain → Verify; Back → exact originating claim; authorized source → deeper analysis then back. |
| Acceptance criteria | Return restores workflow step, scroll/focus, and presentation position; evidence uses the same data snapshot; advisor and manager denominators remain explicit. |
| Common failure mode | Opening a generic analysis page with no route back to the claim. |

## State 10: Historical Items / Historical Reading

| Field | Contract |
| --- | --- |
| User job | Find and reopen the exact dated briefing used previously. |
| Dominant action | **Open briefing**. |
| Secondary actions | Search/filter by business attributes; Create with current data after opening. |
| Visible content | Title, client/audience, generated date, data-as-of date, source template when distinguishing, historical indicator. |
| Hidden content | Run IDs, storage paths, duplicate execution details, generation logs, bulk admin/retention controls. |
| Inputs | Client, meeting, date, presenter, template. |
| Outputs | Selected immutable briefing. |
| Transitions | Open → Historical Reader; Create current → Configuration and a new briefing. |
| Acceptance criteria | Old data is never silently refreshed; generated and data dates are distinguishable. |
| Common failure mode | Treating “refresh” as mutation or turning history into a technical artifact shelf. |

## State 11: External Story Translation Review

| Field | Contract |
| --- | --- |
| User job | Review how an outside narrative has been translated into candidate lenses, scenarios, proxies, and gates without endorsement. |
| Dominant action | **Review next translation item**. |
| Secondary actions | Open evidence; return; complete governance review. |
| Visible content | Story source/summary, persistent translated/not verified/not endorsed/not recommendation status, implied lenses, key-price scenario candidates, gate reasons, governance close. |
| Hidden content | Candidate proxy details except authorized internal review; all fabricated portfolio/lens/scenario outputs; client presentation action by default. |
| Inputs | External story translation pack and approval states. |
| Outputs | Advisor/internal review only; no recommendation or proxy approval. |
| Transitions | Ordered review; gated item detail; governance close → Advisor Review/history. |
| Acceptance criteria | Four unavailable analytic reports remain gated; caveat cannot be dismissed or edited away; no client preview by default. |
| Common failure mode | Treating narrative translation or candidate proxy selection as verified investment guidance. |

## State 12: Developer / QA

| Field | Contract |
| --- | --- |
| User job | Validate schemas, artifacts, source mappings, routes, local storage, and rendering outside the ordinary advisor/client flow. |
| Dominant action | Depends on the selected QA task; no global advisor-facing action. |
| Secondary actions | Copy/download JSON, inspect paths/IDs, load test fixtures, open QA references. |
| Visible content | Technical identifiers, artifact paths, JSON, run/debug details, backend save/load test controls, static reference previews. |
| Hidden content | None required by the advisor information budget; access itself must be separate/protected in future production. |
| Inputs | Technical artifacts and local synthetic fixtures. |
| Outputs | Diagnostic evidence only. |
| Transitions | Explicit return to Home/Advisor Review; never linked as a client presentation step. |
| Acceptance criteria | Not above the fold; not a peer to the four Briefing types; no leakage into Client Preview/Presentation. |
| Common failure mode | Preserving technical capability on the main screen because it already exists. |

## Implementation handoff rule

The later `Advisor Workflow UI Wiring v1` prompt must convert each state above into concrete DOM/component routes and focused tests without adding a new state or user-facing object. Any missing transition or object decision returns to product review rather than being filled with extra UI.
