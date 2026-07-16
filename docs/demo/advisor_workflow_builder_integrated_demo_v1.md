# Advisor Workflow Builder Integrated Demo v1

Status: local handoff and QA record
Date: 2026-07-15
Product: Arangur

## Purpose

This walkthrough verifies that advanced builder capability is restored inside the Conversation Briefing Desk and feeds the same immutable briefing lifecycle. It uses only committed synthetic demo data through June 30, 2026.

## Start

Run the existing local FastAPI application with `src` on the Python path, then open `/app/`. No database, Docker, network service, or external API is required for the ordinary walkthrough.

## Path A — use illustrative as-is

1. On **What conversation are you preparing?**, choose Principal Briefing.
2. Open the built-in template preview and confirm the ordered journey, visibility, optionality, and unavailable-step reasons.
3. Choose **Use this template**.
4. Confirm the fixed synthetic data context and choose **Create briefing with current data**.
5. In Advisor Review, inspect the complete ordered journey and an unavailable placeholder.
6. Open Explain and Verify, then confirm return to the same section.
7. Open Client Preview, advance through the client-only sequence, enter Presentation, and exit.
8. Open history and confirm the created briefing is marked Immutable.

## Path B — deeply customize illustrative

1. Return to Principal Briefing and choose **Customize this template**.
2. In Purpose, change the custom template name and confirm purpose/audience/notes.
3. In Reports, search or filter the combined business catalog. Confirm each card shows report family, question answered, purpose, availability, and visibility. Confirm gated rows are disabled.
4. Add one supported configurable report and one advisor note.
5. In Configure, inspect only supported enumerated parameters and edit the advisor note.
6. In Order & visibility, reorder, duplicate, remove, and set a permitted client-visible section. Confirm advisor-only content cannot be promoted.
7. In Preview, confirm the reusable definition, parameter summaries, order, visibility, optional badges, and caveats.
8. Choose **Save template and create briefing**, then complete Advisor Review → Client Preview → Presentation → history.
9. Confirm the built-in is unchanged and the custom template appears under Saved briefing templates.

## Path C — from scratch

1. On the Desk choose **Build a custom briefing template**.
2. Choose a briefing type and **Start with no sections**.
3. Confirm Reports initially blocks progression until a supported report or narrative section is added.
4. Add, configure, order, preview, and save a reusable template.
5. Create a briefing with current data and complete the current lifecycle.

## External-story path

1. Choose External Manager Story Translation.
2. Confirm governance is visible before template selection, while customizing, in template preview, Advisor Review, and Presentation.
3. Confirm the content is marked translated, not verified, not endorsed, and not a recommendation, and that candidate proxies require approval.
4. Confirm no client-facing path is created by default.

## Design-pattern checks

- Ordinary Desk remains conversation-first; catalog controls appear only after explicit custom-template intent.
- Reader sections are conclusion-first and expose Explain and Verify with exact return.
- Cash sections identify the cash-answer/bridge pattern; scenario sections use a bounded comparison; exposure/lens sections use part-to-whole; attribution/manager/allocation sections keep exact evidence available.
- No Objective Horizon or Plan Check prototype numbers are copied into production defaults.

## Compatibility and Developer / QA

- Open an earlier `arangur.local_named_briefing_workflows.v1` record and confirm it can be customized and resaved.
- Confirm internal IDs, storage keys, schema version, JSON transfer, match diagnostics, and migration status remain confined to Developer / QA or exported JSON.
- Confirm prior local generated-report shelf records and dated briefing history remain readable.

## Automated checks

Run full standard-library discovery:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## Recorded tranche result

- Final full discovery: 445 tests passed in 18.855 seconds.
- Import smoke: `Arangur v2 Demo App` created successfully.
- JavaScript syntax check: passed.
- Diff whitespace check: passed.
- Headless Chrome walkthrough: simple, deep-customize, from-scratch, external-governance, and Developer / QA paths passed.
- Final full-parameter browser check: selected-manager scope revealed the bounded manager selector, accepted a synthetic manager, previewed, and saved successfully.
- Deployment/push: not performed.
