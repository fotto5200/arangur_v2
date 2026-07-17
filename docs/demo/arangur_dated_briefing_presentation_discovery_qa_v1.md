# Arangur Dated Briefing Presentation Discovery QA v1

Status: local implementation and acceptance record
Date: 2026-07-16
Product: Arangur

## Scope

This QA verifies the bounded state, persistence, normalization, and discovery correction for Present a Dated Briefing. It uses the existing non-Docker FastAPI app, committed synthetic data, and a fresh browser-local profile. It does not test a Briefing Section visual redesign, new analytics, production persistence, deployment, or real client data.

## Corrected behavior

- Presentation choices are Choose a Briefing to Present, Preview a Briefing, Start a Presentation, Resume a Presentation, and Find a Briefing.
- Reviewed plus at least one populated audience-visible Briefing Section plus no record-level blocking condition is Preview eligible.
- Ready to Present is accepted only when Preview eligibility passes and is therefore Presentation eligible.
- Resume additionally requires actual saved presentation progress.
- Client uses Client Preview; manager discussion uses Manager Preview; other explicitly presentable audiences use Audience Preview.
- Advisor/internal material without an explicitly saved presentation-visible sequence may be Reviewed but cannot become Ready.
- All state changes normalize/upsert the same Dated Briefing ID and immediately write `arangur.local_briefings.v1`.
- Developer / QA shows record ID, status, audience, section counts, reviewed/ready times, blocking reason, Preview/Presentation/Resume decisions, storage version, and normalization notes.

## Automated focused coverage

`tests/test_dated_briefing_presentation_discovery.py` covers the shared helper stack, status migration guard, all discovery lists, same sequence in reader and eligibility, same-ID persistence, contradictory-state prevention, Resume progress, audience rules, diagnostics, empty states, Find actions, a real generated audience artifact, and preserved advanced capabilities. It runs alongside the existing state/navigation, information-architecture, and workflow-wiring tests.

Recorded result: the focused discovery/state/information-architecture/workflow group passed **53 tests**. Full standard-library discovery passed **486 tests in 28.118 seconds**. Import smoke returned **Arangur v2 Demo App** and `git diff --check` passed.

## Browser acceptance result

A fresh headless Chrome profile ran the product-owner lifecycle locally without Docker:

1. customized and named a Briefing Plan;
2. created one distinctly titled immutable Dated Briefing;
3. completed Advisor Review and marked the same record Ready;
4. found the same ID in Choose, Preview, Start, and Find, but not Resume;
5. confirmed Find exposed Preview and Present;
6. opened Client Preview and the correct record;
7. started Presentation, moved to section 3 of 5, exited to the same section, then resumed section 3;
8. refreshed the browser and repeated Choose/Preview/Start/Resume discovery;
9. restarted the local FastAPI app while preserving the browser-local profile and repeated discovery.

Additional seeded-record checks covered manager discussion, advisor/internal without a sequence, no audience-visible sections, a record-level block, multiple simultaneous records, compatible two-state legacy promotion, uncertain legacy non-promotion, record preservation, ordinary-screen technical-detail exclusion, and Developer / QA migration diagnostics.

Recorded result: **42 browser assertions passed** across the fresh-profile lifecycle and same-profile app restart. Captured browser console and page errors: **0**.

## Persistence result

The named Plan and Dated Briefing were each stored once. Review, ready time, preview time, presentation start/time, and section position remained on the same Dated Briefing record. No duplicate Dated Briefing was created. Discovery survived route changes, Home, browser refresh, and local app restart.

## Legacy result

Compatible older `reviewed` records were promoted only when their stored artifacts proved the shared rule. An older record without an audience sequence and an explicitly ready but blocked record were normalized to Reviewed, retained in storage, and annotated in Developer / QA. Earlier generated-report shelf records remained separate Legacy material.

## Regression result

The advanced Briefing Plan builder, immutable Dated Briefing generation, status model, comparison, Explain/Verify, external-story governance, history, deterministic Ask Arangur, browser-local synthetic persistence, and Developer / QA separation remain. No Briefing Section visual redesign was introduced.

## Commands

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_dated_briefing_presentation_discovery -v
python -m unittest discover -s tests -v
python -c "from arangur.app import app; print(app.title)"
git diff --check
```

## Next tranche

Proceed with **Arangur Dated Briefing Reader and Design-Lab Visual Integration v1** while preserving the corrected lifecycle, eligibility, persistence, audience, and discovery rules.
