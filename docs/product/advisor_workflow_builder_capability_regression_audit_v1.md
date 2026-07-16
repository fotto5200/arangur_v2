# Advisor Workflow Builder Capability Regression Audit v1

Status: implementation baseline recorded before major UI edits; final verification status is updated in this tranche.

Date: 2026-07-15
Product: Arangur
Scope: local synthetic-demo advisor briefing workflow only

## Purpose

This audit compares the capable builder immediately before commit `7bf158d` with the Conversation Briefing Desk introduced by that commit. It is the implementation checklist for restoring advanced composition without weakening the current conversation-first workflow, lifecycle boundaries, or governance.

## Evidence reviewed

- `git show 7bf158d^:src/arangur/app/static/index.html` — earlier report-element composer and reusable named-workflow behavior.
- Current `src/arangur/app/static/index.html` — Conversation Briefing Desk, bounded template builder, dated briefing creation, Advisor Review, Client Preview, Presentation, and immutable browser-local history.
- `src/arangur/report_elements/templates.json` and catalog/rendering code — supported analytic element parameters, branches, placements, scopes, lenses, scenarios, caveats, and preview matching.
- `src/arangur/app/advisor_workflows.py` and committed report-workflow JSON — approved built-in journeys, status, visibility, optionality, gating, and preview availability.
- Canonical product, report-family, information-budget, data-boundary, and design-lab documents under `docs/`.

## Finding

The Conversation Briefing Desk improved the dominant advisor journey and correctly separated reusable templates from immutable dated briefings. Its bounded editor intentionally removed most of the capable composer. The restoration therefore belongs behind progressive disclosure in the Desk, not as a return to a dense default home screen and not as a second lifecycle.

## Capability comparison and tranche disposition

| Capability | Earlier capable builder | Current Desk baseline | Required integrated behavior | Status after tranche | Verification |
|---|---|---|---|---|---|
| Conversation-first home | Composer was the primary surface | Four briefing types lead the home experience | Preserve the current home and add one secondary custom-template entry | Restored and verified | Browser: home and from-scratch entry passed |
| Use illustrative template as-is | Named workflows could be opened/generated | Built-ins can be selected and used | Keep the short template-to-current-data path | Restored and verified | Browser: simple path passed through Presentation |
| Deeply customize illustrative template | Built-ins could be opened as working copies in the composer | Built-ins can only be duplicated into a bounded editor | Open a full staged draft with existing sections and choices preserved | Restored and verified | Browser: deep path passed |
| Start from scratch | New client/advisor workflow actions started empty sets | No Desk-native empty-template path | Create an empty reusable draft within a chosen briefing type | Restored and verified | Browser: from-scratch path passed |
| Reusable template naming | Named local workflows supported create/rename/save-as | Bounded copy has a template name | Preserve unique reusable naming and local persistence | Restored and verified | Automated static contract + browser save passed |
| Briefing purpose | Workflow payload and narrative supported context | Bounded editor exposes purpose | Make purpose the first builder decision and preview it | Restored and verified | Browser stages and preview passed |
| Audience/depth | Branch selection and placements encoded audience | Bounded editor has one audience selector | Keep plain-language audience/depth choices with approved visibility bounds | Restored and verified | Automated visibility checks + browser passed |
| Catalog discovery | Search, category, topic, browse-all, client question, advisor intent | Not available in Desk builder | Restore search, family filters, questions, purposes, status, and visibility | Restored and verified | Automated catalog contract + deep browser path passed |
| Add analytic report | Catalog preview/configure/add flow | Only existing built-in steps can be included | Add available catalog reports into the reusable draft | Restored and verified | Browser added configurable report |
| Add narrative section | Nine client/advisor narrative types with field validation | Not available in Desk builder | Restore plain-language narrative additions with audience-safe placements | Restored and verified | Automated action/configuration contract |
| Edit report configuration | Existing specs reopened in configuration mode | No per-report editing | Edit only supported catalog parameters and approved choices | Restored and verified | Automated parameter contract + browser Configure stage |
| Full supported parameter set | Branch, placement, scope, lens, metric, scenario, selected entity, and optional fields | Bounded editor exposes none | Restore supported parameters; never invent analytical defaults | Restored and verified | Parameter contract + catalog tests |
| Visibility controls | Client and advisor sets were independently composed | Per-row client-visible toggle, bounded by type | Preserve bounds and expose visibility during configuration and preview | Restored and verified | Automated + browser order/visibility stage |
| Optional/gated semantics | Catalog readiness and preview matching were available | Optional/gated semantics are visible | Preserve unavailable steps as explanatory placeholders, never generated results | Restored and verified | Existing gated generation tests + browser catalog |
| Reorder sections | Move up/down on both sets | Move up/down in bounded journey | Preserve ordering in staged builder and generated artifacts | Restored and verified | Automated action contract + browser stage |
| Duplicate section | Duplicate action existed on composed specs | Not available | Restore duplication with a new local section identity | Restored and verified | Browser duplication passed |
| Remove section | Remove action existed | Optional steps can be unchecked; required cannot be removed | Restore remove for custom composition while keeping required built-in context when appropriate | Restored and verified | Automated action contract |
| Template preview | Set previews and rendered-view matching existed | Journey-only template preview | Show purpose, order, visibility, supported choices, optional/gated state, and caveats | Restored and verified | Browser preview passed |
| Save and create | Named workflows were saved separately from generated reports | Bounded save flows directly to current-data configuration | Preserve a dominant Save template and Create briefing path | Restored and verified | Browser: deep and scratch save paths passed |
| Lifecycle continuity | Composer generated local report artifacts | Template → dated briefing → review/preview/presentation/history exists | Route every builder path into the current lifecycle | Restored and verified | Focused generation tests + browser simple/deep paths |
| Existing local-record compatibility | Named-workflow schema and JSON import/export existed | Loader normalizes older workflow records | Continue reading prior records and migrate missing editor metadata at runtime | Restored and verified | Automated compatibility-shape check |
| Developer QA | Dense composer exposed technical matching and export tools | Existing Advanced/Developer tools remain available | Keep technical identifiers and migration diagnostics out of advisor mode | Restored and verified | Browser: Developer / QA path passed |
| External-story governance | External workflow caveats existed in its built-in | Desk repeats translated/not verified/not endorsed boundaries | Preserve caveats throughout customize, preview, review, and presentation | Restored and verified | Existing governance tests + browser external path |
| Report-family presentation patterns | Generic rendered fragments and tables | Generated sections retain committed report content | Add conclusion-first family framing without copying design-lab values or inventing analytics | Restored and verified | Automated no-leak/pattern check + browser reader |

## Non-regression rules

1. The default home remains the Conversation Briefing Desk.
2. Builder stages create or edit reusable template definitions only.
3. `Create briefing with current data` creates a new immutable dated record.
4. Advisor Review precedes Client Preview and Presentation for client-facing work.
5. Gated or deferred outputs remain clearly unavailable; no fake result is generated.
6. External-story content remains translated, unverified, unendorsed, and not a recommendation.
7. Design-lab values, tolerances, objectives, and scenario numbers are interaction examples only and cannot become production defaults.
8. Internal IDs, storage keys, source paths, matching state, and migration details stay in Developer QA.

## Implementation acceptance rule

Every row is restored and verified in this tranche. Exact full-discovery and browser results are recorded in the commit packet and `docs/demo/advisor_workflow_builder_integrated_demo_v1.md`.
