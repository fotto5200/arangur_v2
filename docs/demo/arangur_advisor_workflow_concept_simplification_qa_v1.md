# Arangur Advisor Workflow Concept Simplification QA v1

Status: local implementation and acceptance record
Date: 2026-07-16
Product: Arangur

## Scope

This QA covers the ordinary advisor menu and lifecycle simplification while preserving the advanced builder, immutable Dated Briefings, selected presentation sequence, browser-local records, external-story governance, and Developer / QA. It excludes populated-section visual redesign, new analytics, Docker, deployment, external APIs, real data, and production persistence.

## Automated coverage

`tests/test_advisor_workflow_concept_simplification.py` covers:

- exactly four primary activities and two secondary shortcuts;
- exactly two Prepare choices;
- one contextual Existing library and object-specific actions;
- comparison exclusion from ordinary UI;
- one searchable Present list;
- content-first Dated Briefing opening;
- presentation without Review or Ready gates;
- full populated-presentable default selection;
- protected/unavailable exclusion and saved custom ordering;
- exact Presentation exit context;
- contextual More Detail and direct attribution tables;
- one Ask Arangur prompt and safe deterministic routing;
- legacy/storage/diagnostic preservation;
- advanced builder, immutable generation, history, and governance regressions.

The earlier workbench, discovery, selection, workflow-wiring, and app-health suites were updated where their old ordinary-menu assertions were superseded. They continue to protect the underlying implementation and compatibility paths.

## Browser acceptance checklist

Use a fresh local browser profile and start the non-Docker app:

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn arangur.app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/app/`.

### Prepare

1. Confirm Prepare contains only Build from Scratch and Start from a Template.
2. Open the full builder from scratch and confirm all five stages and existing section/configuration controls.
3. Open the template library and exercise Use and Customize.

### Existing

1. Confirm one mixed Draft, My Saved Plan, and Dated Briefing library.
2. Continue a Draft; revise a saved Plan; create a Dated Briefing.
3. Open a Dated Briefing and confirm the first populated presentable section appears immediately.
4. Confirm Open, Create Updated Dated Briefing, and Present are contextual Dated Briefing actions.
5. Confirm comparison has no ordinary menu entry.

### Present

1. Open Present a Dated Briefing and confirm one searchable list.
2. Select a Dated Briefing and present immediately without Review, Preview, or Ready steps.
3. Confirm Previous, Next, position, Exit, and same-section return.
4. Open Choose Sections, remove and reorder sections, save, and confirm Presentation uses the saved sequence.

### Ask Arangur

1. Confirm one prompt and five example requests.
2. Exercise creation, find, update, manager-meeting, and Briefing Plan explanation routing.
3. Confirm no external-AI or investment-recommendation claim.

### Compatibility and boundaries

1. Refresh and restart the local app with the same browser profile.
2. Confirm Drafts, saved Plans, Dated Briefings, saved selection/order, and progress remain.
3. Confirm obsolete lifecycle statuses do not block Present.
4. Confirm protected/unavailable sections remain excluded.
5. Confirm ordinary screens expose no raw IDs, JSON, paths, schemas, readiness diagnostics, universal Explain, or universal Verify.
6. Confirm Developer / QA retains storage, migration, old-status, eligibility, and selection diagnostics.
7. Confirm no browser console or page errors.

## Acceptance result

The final automated and browser results for this tranche are recorded in the implementing commit and consolidated completion packet. The next visual tranche remains **Arangur Dated Briefing Reader and Design-Lab Visual Integration v1**.
