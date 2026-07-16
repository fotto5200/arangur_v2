# Arangur Advisor Workbench Information Architecture Demo v1

Status: local implementation and QA handoff
Date: 2026-07-16
Product: Arangur

## Implemented home

The ordinary home asks **What would you like to do?** and shows exactly four primary activities: Prepare a New Briefing Plan; Work with Existing Plans or Briefings; Present a Dated Briefing; Ask Arangur. Recent Work, Ready to Present, and Recent Dated Briefings are secondary shortcuts. Developer / QA is a footer action.

The four illustrative workflows no longer appear as top-level peers. They are labeled Arangur example Briefing Plan Templates inside the template library.

## Canonical vocabulary and object behavior

The ordinary workbench uses Briefing Plan, Briefing Plan Draft, Briefing Plan Template, Dated Briefing, and Briefing Section. The relationship is **Briefing Plan + Current Data = Dated Briefing**.

Drafts continue at the exact stored builder stage. Saved plans revise or copy. Dated Briefings open to populated content. Reviewed Dated Briefings become Ready to Present.

## Second-level menus

- Prepare: build new; template library; prior plan; continue draft.
- Existing: revise/continue; create Dated Briefing; compare; view.
- Present: ready list; audience preview; launch; resume; find.
- Ask Arangur: seven deterministic help/routing choices.

## Legacy migration behavior

Recognizable earlier saved-workflow records normalize on read. Incompatible records are retained, classified Legacy, hidden from ordinary current lists, and shown in Developer / QA. Earlier generated-report shelf records are also retained as Legacy. Nothing is silently deleted.

## Ask Arangur boundary

Ask Arangur uses local product rules and current browser-local metadata. It does not connect to an external AI service, invent data or Briefing Sections, make investment recommendations, or bypass gated behavior.

## Local run instructions

From the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn arangur.app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/app/`. Docker, a database, external APIs, and dependency installation are not required.

## Manual QA walkthrough

### Home

1. Confirm the four primary activities and concise copy.
2. Confirm example workflow names are absent from the home.
3. Confirm the three secondary shortcuts and footer Developer / QA.

### Prepare a New Briefing Plan

1. Open Build a new briefing plan; choose Client, enter a purpose, choose detail, and continue to Briefing Sections.
2. Add/configure/reorder Briefing Sections and save the plan.
3. Open the template library; confirm four Arangur examples plus advisor-created templates; use and customize an example.
4. Open prior plans and exercise same-plan and revise-first paths.
5. Leave a draft, reopen Drafts, and confirm its exact stage.

### Work with Existing Plans or Briefings

1. Confirm the mixed status-aware plan list.
2. Continue a draft and revise/copy a saved plan.
3. Create a Dated Briefing from a plan and confirm Advisor Review opens an actual populated Briefing Section.
4. View a prior Dated Briefing and confirm the same content-first behavior.
5. Select two Dated Briefings for comparison and confirm unsupported historical reconstruction is explicitly not inferred.

### Present a Dated Briefing

1. Complete Advisor Review and confirm Ready to Present.
2. Start Client Preview and navigate Previous/Next.
3. Launch Presentation and confirm clean content-first presentation.
4. Exit, open Resume, and confirm the saved Briefing Section position.
5. Find a briefing using supported saved metadata.

### Ask Arangur

1. Open each of the seven guidance choices.
2. Confirm buttons route into the real Prepare, Existing, Present, Plan, and Dated Briefing states.
3. Confirm the interface states its deterministic/local and no-investment-recommendation boundary.

### Legacy and regression

1. Seed a recognizable older named-workflow record and confirm it remains usable.
2. Seed an incompatible record and confirm it is absent from ordinary lists but shown in Developer / QA.
3. Confirm the advanced builder, parameters, Advisor Review, Client Preview, Presentation, Explain/Verify, history, external-story caveats, and honest unavailable output behavior remain intact.

## Automated checks

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_advisor_workbench_information_architecture -v
python -m unittest discover -s tests -v
python -c "from arangur.app import app; print(app.title)"
git diff --check
```

## Recorded acceptance result — 2026-07-16

- Focused information-architecture, wiring, health, and embedded-JavaScript checks: **34 passed**.
- Complete repository suite: **457 passed in 23.541 seconds**.
- Fresh-profile headless Chrome lifecycle: **22 checks passed**, including exact-stage draft resume, example customization, two immutable Dated Briefings, populated-section-first Advisor Review, Ready to Present, audience filtering, presentation time/position persistence, honest comparison, deterministic Ask Arangur, and compatible/incompatible legacy handling.
- Captured browser/console errors during the lifecycle: **0**.
- Desktop visual inspection at 1440 × 1100 confirmed exactly four balanced primary activities, subordinate shortcuts and Developer / QA, and the four example templates below the top level with approachable metadata and equally available Use as is / Customize actions.
- Direct hash-route smoke coverage passed for home, Prepare, template library, Existing, Present, Ask Arangur, new-plan setup, comparison, and Developer / QA.

## Known limitations

- Browser-local persistence is a synthetic-demo approximation, not production tenancy, audit, sharing, or retention.
- Comparison shows only information stored in the two Dated Briefing artifacts. It does not reconstruct unavailable historical positions or values.
- Ask Arangur is deterministic routing, not live AI analysis.
- Current data remains the fixed synthetic snapshot through June 30, 2026.

## Explicitly deferred reader redesign

This tranche changes entry and navigation so a Dated Briefing opens populated Briefing Sections. It does not redesign those populated visuals. Design-lab HTML prototypes remain context only.

Recommended next tranche: **Arangur Dated Briefing Reader and Design-Lab Visual Integration v1**.
