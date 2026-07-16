# Arangur Advisor Workbench State and Navigation QA v1

Status: local implementation and acceptance record
Date: 2026-07-16
Product: Arangur

## Scope

This walkthrough verifies the bounded state/navigation correction against a fresh browser-local profile. It does not validate a Briefing Section visual redesign, production persistence, export/sharing, live AI, real data, or deployment.

## Local run

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn arangur.app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/app/` with a fresh profile.

## Acceptance checklist

### Selection and template customization

- Included and Available groups render separately with a persistent Current Briefing Plan outline.
- Add immediately updates the labeled included row, live count, and outline.
- Remove immediately decrements the count and returns the section to Available.
- Existing template sections show order, visibility, optional/required state, and configuration summary.
- Manager Comparison can be added at the next visible position, removed, and re-added.
- Configure, Order & visibility, Preview, and Save retain the selected section and choices.

### Drafts and saved plans

- Opening and leaving setup without a meaningful choice creates no persisted Draft.
- A meaningful Draft stores temporary name, audience, created/edited time, exact stage, section count, Autosaved state, and source lineage where applicable.
- Continue restores the Briefing Sections stage and selected count.
- Discard Draft prompts for confirmation and removes only the selected Draft.
- Saved plans show dates, lineage, count, latest Dated Briefing where present, and Revise/Duplicate/Create/Archive actions.

### Dated Briefings and status

- The suggested Dated Briefing title is meaningful and editable.
- Distinct titles remain distinct in lists with audience, briefing/data dates, source Plan, status, count, and activity.
- Complete Advisor Review moves Dated Briefing to Reviewed.
- Reviewed client/manager material is previewable before it is presentable.
- Mark Ready to Present is available only for a previewable audience sequence.
- Advisor/internal material without an audience-visible sequence remains excluded from Preview and Presentation eligibility.
- Client and Manager preview wording follows audience type.

### Presentation and navigation

- Presentation hides authoring/review controls.
- Exiting section 3 of one Dated Briefing returns to section 3 of the same Dated Briefing in Preview.
- Launching a second Dated Briefing does not replace the first record's saved position.
- Resume reopens the first Dated Briefing at its own saved section.
- Back routes are explicit; Ask Arangur destinations return to Ask Arangur.
- Explain/Verify remains bound to the current section and returns in context.

### Comparison and empty states

- Two selections remain visible and comparison does not run automatically.
- Compare Briefings is required.
- Supported common/unique/configuration differences are shown without reconstructing history.
- A no-common-section comparison shows the required explanation, both unique lists, and the similar-Plan suggestion.
- Draft, comparison, ready, and preview empty states are actionable and use ordinary language.

## Recorded browser result

A fresh headless Chrome profile was exercised locally on 2026-07-16. The walkthrough passed setup-without-Draft, real Draft autosave/resume/discard, immediate add/remove/count/outline feedback, Advisor Oversight template customization, saved Plan identity, editable Dated Briefing naming, internal Reviewed behavior, Client Preview-before-Presentation behavior, Ready-to-Present transition, clean Presentation, exact exit to section 3 of 5, a second Dated Briefing without context mixing, resume of the first at section 3 of 5, Ready/Preview/Launch/Find consistency, Manager Preview wording, explicit comparison, no-common-section explanation, unique-section lists, and Ask Arangur return routing. Captured browser console and page errors: 0.

Focused state/navigation, information-architecture, workflow-wiring, and embedded-JavaScript checks: **40 passed**. Full standard-library discovery: **472 passed in 16.375 seconds**. Import smoke returned **Arangur v2 Demo App** and `git diff --check` passed.

## Automated checks

The focused correction contract is in `tests/test_advisor_workbench_state_navigation_correction.py`. Standard checks are:

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_advisor_workbench_state_navigation_correction -v
python -m unittest discover -s tests -v
python -c "from arangur.app import app; print(app.title)"
git diff --check
```

## Deferred work

Populated Briefing Section visual redesign remains deferred to **Arangur Dated Briefing Reader and Design-Lab Visual Integration v1**.
