# Arangur UI Design Lab v1

## Status

This directory contains imported **design inputs, interaction studies, visual experiments, and HTML prototypes** for the Arangur advisor and client user experience.

These files are important project evidence, but they are **not automatically the canonical product specification** and are not production application code.

Accepted product decisions must be promoted into the appropriate canonical documents under:

- `docs/product/`
- `docs/project_control/`
- `docs/architecture/`
- `docs/contracts/`

before implementation.

## Canonical product name

The product name is **Arangur**.

“Arranger” in older notes is a voice-transcription or historical artifact unless it appears in an existing filename, path, or other preserved source material.

Do not propagate “Arranger” into new product prose.

Do not rename historical files solely to correct the old wording unless a separate migration is explicitly approved.

## Original source

Original working directory:

```text
C:\Users\fotto\cursor\Arangur UI Design Lab
```

Imported repository location:

```text
docs/design_inputs/arangur_ui_design_lab_v1/
```

The original external directory should remain intact as a working archive.

This repository directory is a version-controlled snapshot of the design material available at the time of import.

## Import purpose

The design lab is being preserved inside the Arangur repository so that future work can reliably access:

- advisor workflow requirements;
- client-report interaction concepts;
- alternative application architectures;
- simplified UI principles;
- briefing and template lifecycle proposals;
- evidence, explanation, and verification patterns;
- report-family visual experiments;
- HTML interaction prototypes;
- selected, rejected, provisional, and unresolved design directions.

The immediate reason for importing these materials is to help reconcile:

1. the current Conversation Briefing Desk;
2. the earlier, more capable workflow and report builder;
3. the newer UI design-lab interaction approach;
4. the accepted report and workflow catalog;
5. the need to preserve full advisor customization through progressive disclosure.

## Interpretation rules

Use the following rules when reading or implementing from this directory.

### 1. Design input is not automatic approval

A file in this directory may represent:

- an accepted principle;
- a candidate approach;
- a comparison alternative;
- a provisional refinement;
- a superseded direction;
- a disposable prototype;
- an unresolved product decision.

Do not assume that the newest or most visually polished file is approved.

### 2. Do not silently combine competing architectures

The design lab may contain alternative application structures such as:

- Briefing Desk;
- Arangur Guide;
- Investment Library;
- Plan Check;
- Objective Horizon;
- Wealth Journey;
- Stewardship Brief.

Do not combine these into a hybrid architecture without:

1. identifying the user job served by each borrowed element;
2. explaining why the selected primary architecture is insufficient by itself;
3. documenting the resulting design explicitly;
4. obtaining Frank’s approval;
5. recording the decision in the project-control documents.

### 3. HTML files are prototypes, not production code

HTML files in this directory are visual and interaction specimens.

They may be used to understand:

- layout;
- screen hierarchy;
- progressive disclosure;
- navigation;
- report explanation;
- verification behavior;
- contextual return;
- presentation flow.

They should not be copied wholesale into the application without a deliberate implementation plan.

Their sample values, labels, thresholds, and data may be illustrative rather than valid client facts.

### 4. Preserve capability while simplifying access

The governing UI principle is:

> Progressive disclosure, not capability removal.

The target advisor experience should support:

- using an illustrative briefing workflow as provided;
- deeply customizing an illustrative workflow;
- creating a new reusable briefing template from approved reports;
- selecting and ordering reports;
- configuring supported report parameters;
- choosing lenses, scenarios, managers, benchmarks, time periods, and presentation depth where supported;
- controlling advisor-only versus client-visible material;
- saving reusable templates;
- generating immutable dated briefings;
- conducting Advisor Review;
- entering Client Preview;
- presenting a clean client-facing briefing.

Simplification should affect how capabilities are introduced and organized, not remove approved functionality.

### 5. Keep user surfaces distinct

Arangur has several separate surfaces:

- Advisor workflow and briefing construction;
- Advisor Review;
- Client Preview;
- Presentation;
- Historical briefing reading;
- Developer / QA;
- Private client-data execution;
- Internal analytics control plane.

Do not expose technical, administrative, or analytics-construction controls in ordinary advisor or client states.

### 6. Protect accepted analytics boundaries

UI work must preserve existing product decisions, including:

- full portfolio revaluation as the scenario-impact methodology;
- lenses classify and explain after valuation rather than price positions;
- advisor policy attribution remains separate from manager implementation attribution;
- equal-weight attribution is diagnostic unless explicitly adopted as policy;
- external manager stories are translated, not verified or endorsed;
- candidate benchmark and proxy mappings require approval;
- gated analytics must not be fabricated.

### 7. Do not expose internal artifacts

Ordinary advisor and client screens should not display:

- raw JSON;
- schema names;
- internal IDs;
- source paths;
- fixture filenames;
- run identifiers;
- implementation terminology;
- debug information.

These may remain available in Developer / QA views.

## Source-of-truth hierarchy

Use this hierarchy when materials conflict:

1. Current implemented code and tests;
2. Current accepted contracts and product documents;
3. Current project-control decision register;
4. Approved UI integration blueprint;
5. Imported UI design-lab evidence;
6. Older tactical notes and historical prototypes.

Do not resolve conflicts silently.

Record discrepancies and request a decision where needed.

## Promotion process

Before implementing a design-lab idea:

1. identify the relevant source file;
2. summarize the proposed design decision;
3. classify it as accepted, candidate, superseded, deferred, or requiring review;
4. compare it with current application behavior and accepted product contracts;
5. record the approved decision in `docs/project_control/`;
6. update the appropriate canonical specification in `docs/product/`;
7. define implementation acceptance criteria;
8. implement and test in a separate bounded tranche.

## Current integration objective

The next integration work should reconcile the design lab with both:

- the current simplified Conversation Briefing Desk; and
- the earlier, more capable workflow/report builder.

The target experience should retain the clean conversation-first entry while restoring substantive workflow construction through a progressively disclosed advanced builder.

A future capability matrix should identify:

| Capability | Previously available | Available now | Required target behavior | Simple path | Advanced path | Design-lab source | Test required |
|---|---:|---:|---|---|---|---|---|
| Choose an illustrative briefing |  |  |  |  |  |  |  |
| Duplicate and customize a template |  |  |  |  |  |  |  |
| Create a custom briefing template |  |  |  |  |  |  |  |
| Select reports from the approved catalog |  |  |  |  |  |  |  |
| Configure report parameters |  |  |  |  |  |  |  |
| Reorder report journey |  |  |  |  |  |  |  |
| Set advisor/client visibility |  |  |  |  |  |  |  |
| Configure lenses and scenarios |  |  |  |  |  |  |  |
| Generate a dated briefing |  |  |  |  |  |  |  |
| Conduct Advisor Review |  |  |  |  |  |  |  |
| Preview client-visible content |  |  |  |  |  |  |  |
| Present the briefing |  |  |  |  |  |  |  |

## Known design directions

The following status should be treated as the current working interpretation unless later project-control documents supersede it:

- **Conversation Briefing Desk** — current implemented application architecture.
- **Plan Check** — selected for the first client-facing “How am I doing?” story only.
- **Objective Horizon** — preferred refinement direction, but not a frozen global visual system.
- **Briefing Desk / Arangur Guide / Investment Library** — alternative application concepts whose useful elements require explicit reconciliation.
- **Wealth Journey / Stewardship Brief** — comparison inputs, not selected primary directions.
- **Old dense console** — superseded as the ordinary advisor experience, though some capabilities may belong in advanced or Developer / QA states.
- **One-report wizard** — superseded as the complete workflow model, though its progressive-disclosure discipline remains valuable.

## Refreshing this snapshot

When the external design-lab directory changes materially:

1. review the new files;
2. confirm that no secrets, temporary browser data, or irrelevant large files are included;
3. copy the updated material into this directory while preserving relative paths;
4. update this README with the refresh date and a summary;
5. review the Git diff carefully;
6. update the project-control inventory;
7. commit the refreshed snapshot separately from application implementation.

## Import record

- **Imported from:** `C:\Users\fotto\cursor\Arangur UI Design Lab`
- **Imported into:** `docs/design_inputs/arangur_ui_design_lab_v1/`
- **Import date:** 2026-07-15
- **Imported by:** Codex bounded advisor-workflow builder integration tranche
- **Source status:** External working design archive
- **Repository status:** Version-controlled design input
- **Canonical implementation authority:** No
- **Secrets reviewed before commit:** Yes; no credentials, browser profiles, live client data, or external service configuration found
- **Relative HTML assets preserved:** Yes; the two prototypes are self-contained and no separate relative asset files were present

## Integration status — 2026-07-15

The capability/conflict audit is now canonical at `docs/product/advisor_workflow_builder_capability_regression_audit_v1.md`. The promoted product decisions and parameter bounds are recorded in:

- `docs/product/advisor_workflow_builder_restoration_and_integration_v1.md`
- `docs/product/advisor_workflow_builder_parameter_contract_v1.md`
- `docs/demo/advisor_workflow_builder_integrated_demo_v1.md`

Promoted patterns are progressive disclosure without capability removal, one dominant action per builder stage, conclusion-first reporting, Explain/Verify with exact contextual return, and report-family framing that preserves exact committed evidence. Prototype-only client objectives, tolerances, thresholds, ranges, and scenario values were not promoted.

## Inventory

Add or update this table after import:

| File | Type | Purpose | Current status | Implementation relevance |
|---|---|---|---|---|
| `ARANGUR_UI_DESIGN_LAB_INSTRUCTIONS.md` | Markdown | Design constitution and stage gates | Design input | High |
| `arangur_ui_user_jobs_v1.md` | Markdown | User jobs and object/lifecycle proposals | Design input | High |
| `arangur_ui_interaction_directions_v1.md` | Markdown | Alternative application architectures | Requires review | High |
| `arangur_ui_client_report_how_am_i_doing_packet_v1.md` | Markdown | First client-report interaction direction | Partially selected | High |
| `arangur_ui_selected_direction_v1.md` | Markdown | Selected report-story scope | Provisional | High |
| `arangur_ui_plan_check_visual_concepts_v1.md` | Markdown | Visual alternatives | Candidate/reference | Medium |
| `arangur_ui_objective_horizon_manager_refinement_v1.md` | Markdown | Portfolio-to-manager interaction refinement | Preferred refinement | High |
| `arangur_ui_report_breadth_test_v1.md` | Markdown | Cross-report visual-language test | Design evidence | High |
| `arangur_objective_horizon_manager_refinement_v1.html` | HTML | Interactive report prototype | Prototype only | High |
| `arangur_report_breadth_test_v1.html` | HTML | Cross-report prototype | Prototype only | High |

Add any additional files and assets discovered during import.

## Do not build directly from this directory

This directory should inform design and implementation, but production work should be based on an approved canonical contract under `docs/product/`.

The expected sequence is:

```text
Design input
→ capability and conflict audit
→ Frank review
→ canonical product contract
→ bounded implementation prompt
→ tests and browser QA
→ project-control update
```
