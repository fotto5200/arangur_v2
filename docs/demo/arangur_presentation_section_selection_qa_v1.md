# Arangur Presentation Section Selection QA v1

Status: local implementation and acceptance record
Date: 2026-07-16
Product: Arangur

## Scope

This QA verifies advisor-controlled selection, audience defaults, protected/unavailable classification, exact Preview/Presentation order, readiness, discovery, browser-local persistence, legacy compatibility, and external-story governance. It uses the non-Docker local FastAPI app, committed synthetic data, and a fresh browser-local Edge profile.

## Automated coverage

`tests/test_presentation_section_selection.py` executes the deterministic JavaScript helper stack with client, manager, advisor/internal, protected, unavailable, and external-story records. It also verifies the selection surface, record fields, migration guard, shared discovery filters, empty states, diagnostics, and regression boundaries.

Recorded focused result: **49 tests passed** across the new selection module and the existing presentation-discovery, state/navigation, and information-architecture modules.

Recorded full result: **494 tests passed**. Import smoke returned **Arangur v2 Demo App**, and `git diff --check` passed.

## Browser acceptance

A fresh persistent headless Edge profile exercised real generated Dated Briefings locally:

- Client: confirmed client defaults; included Coverage and Confidence Warning as an advisor-oriented section; excluded a client default; reordered; saved; confirmed Preview and Presentation matched the five-section saved sequence; marked Ready; exited with section context preserved.
- Advisor/internal: created Advisor Oversight; reduced the selection to one advisor policy attribution section; Previewed, marked Ready, and presented successfully.
- Manager discussion: opened a manager-discussion Dated Briefing derived from a real populated Advisor Oversight artifact; confirmed manager defaults, Manager Preview wording, readiness, and Presentation.
- External Manager Story Translation: confirmed Manager Story Summary and Governance/Caveat Note defaults; confirmed Implied Lenses, Key-Price Scenario Set, and Candidate Benchmark/Proxy Map were protected; confirmed four gated outputs were unavailable; confirmed all five governance caveats.
- Persistence/discovery: confirmed saved order through Home/list navigation and browser refresh; restarted the local FastAPI app with the same browser profile; then confirmed the same record and selection under Choose, Preview, Start, Resume, and Find.

Recorded result: **33 browser assertions passed** in two phases (26 before restart and 7 after restart). Captured browser console and page errors: **0**.

## Regression and boundary result

The advanced builder, immutable Dated Briefing generation, Advisor Review, comparison, Ask Arangur, Explain/Verify, exit/resume context, external governance, legacy retention, and Developer / QA separation remain. No populated Briefing Section visual redesign, analytics, dependency, Docker, deployment, external API, live AI, real-data, or production-persistence change was introduced.

## Commands

```powershell
$env:PYTHONPATH = "src"
python -m unittest tests.test_presentation_section_selection -v
python -m unittest discover -s tests -v
python -c "from arangur.app import app; print(app.title)"
git diff --check
```

## Next tranche

Proceed with **Arangur Dated Briefing Reader and Design-Lab Visual Integration v1**, preserving the saved selection, eligibility, protected-material, persistence, governance, and exact-sequence contracts.
