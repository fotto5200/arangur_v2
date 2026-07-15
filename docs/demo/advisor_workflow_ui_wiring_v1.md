# Advisor Workflow UI Wiring v1

Status: implemented local synthetic-demo tranche, 2026-07-15

## Architecture implemented

The advisor demo now uses the approved **Conversation Briefing Desk** architecture. The first screen asks **“What conversation are you preparing?”** and treats the four committed catalog definitions as business-language Briefing types. Once current synthetic data is used, the dated Briefing becomes the center of Advisor Review, Client Preview, Presentation, Explain/Verify, and historical reopening.

The implementation reuses the existing FastAPI catalog adapter, committed report mockups, generated-report population service, static rendering helpers, browser-local template store, and legacy generated-report shelf. No analytics, report methodology, dependency, Docker, deployment, live-data, or real-client-data changes were made.

## User-facing vocabulary

- Catalog workflow: **Briefing type**
- Reusable definition: **Briefing template**
- Generated dated output: **Briefing**
- Internal inspection and approval: **Advisor Review**
- Exact rehearsal of client-visible content: **Client Preview**
- Audience-facing delivery: **Presentation**
- Contextual support: **Explain** and **Verify**
- Missing prerequisite: **Not yet available** plus a plain-language reason

Raw workflow IDs, report IDs, paths, JSON/schema language, artifact details, and technical gate codes stay outside the ordinary advisor/client states.

## Supported states

The hash-routed local app supports:

1. Conversation Briefing Desk home
2. Briefing-type detail and template selection
3. Briefing-template preview
4. Bounded custom-template builder
5. Briefing configuration
6. Advisor Review
7. Client Preview
8. Presentation
9. Explain / Verify depth with return to the same section
10. Browser-local briefing history
11. Separate Developer / QA route with the prior technical composer and transfer tools

## Four briefing types

### Principal / Family Office Briefing

Client-facing minimal journey covering representation, delivered cash, cash outlook, broad allocation, and scenario downside. Coverage/confidence stays in Advisor Review, and the unavailable advisor-plan step is shown internally as not yet available without a fabricated report.

### Engaged Client / Investment Committee Review

Sophisticated client/committee journey covering allocation, advisor responsibility, manager responsibility, lens exposure, and scenario downside. Advisor-review attribution and dense manager depth remain excluded from the client sequence unless a bounded custom template explicitly makes an approved advisor-review section client-visible.

### Advisor / Manager Oversight

Advisor/internal journey covering drift, benchmark basis, separate advisor and manager attribution, the exact Manager Driver Attribution Matrix, selected-manager depth, handoff control, coverage, and the gated manager-coverage step. It does not create a Client Preview by default.

### External Manager Story Translation

Advisor/internal translation journey. Every ordinary external-story state carries:

- Translated external viewpoint
- Not verified
- Not endorsed
- Not a recommendation
- Candidate proxies require approval

Candidate proxy detail stays internal. The four unavailable analytic outputs remain gated and are never generated as portfolio, manager, scenario, or scenario-by-lens results.

## Template and bounded-builder behavior

Built-ins remain read-only. **Duplicate** creates a custom working copy with a new browser-local identity. The bounded builder allows:

- template name;
- audience/depth selection from a short approved set;
- briefing purpose;
- material notes/caveats;
- optional approved-section inclusion;
- approved report order;
- client visibility only where the source visibility contract permits it.

Primary and gated journey steps remain in context. External-story governance cannot be removed. The former unconstrained report-element composer remains available only through Developer / QA for compatibility and testing.

## Dated briefing lifecycle

**Create briefing with current data** calls the existing local generated-report population endpoint for the Advisor Review sequence and, when allowed, the filtered client sequence. It creates one compound browser-local briefing with:

- a unique briefing identity;
- generated timestamp;
- fixed synthetic data date;
- Briefing type and template lineage;
- immutable Advisor Review artifact;
- immutable client artifact when the Briefing type permits one;
- the ordered journey and governance caveats.

Repeating current-data creation adds a new Briefing. Prior Briefings and their fixed dates/content remain unchanged. Editing a custom template affects only future Briefings.

## Browser-local persistence

- Custom Briefing templates continue to use `arangur.local_named_briefing_workflows.v1`.
- New compound dated Briefings use `arangur.local_briefings.v1`.
- Earlier generated-report records under `arangur.local_generated_reports.v1` remain readable as legacy history.

This is demo-only device-local persistence. There is no production tenancy, retention, audit, sharing, or durable backend Briefing store.

## Advisor Review

Advisor Review shows the fixed title, generated/data dates, audience, complete ordered journey, visibility classification, optionality, material caveats, report content, and calm gated-step explanations. Gated sections render as unavailable placeholders internally and are explicitly identified as not fabricated. Changes that require different content direct the advisor back to the reusable template and a new Briefing.

## Client Preview and Presentation

Client Preview reads only the generated client artifact. Advisor-only, advisor-review-by-default, setup/readiness, diagnostic, internal-control, gated, proxy-candidate, generation, template, and developer material cannot be reached through client navigation.

Presentation uses the same section order/content as Client Preview with reduced chrome: Arangur branding, fixed Briefing/data dates, current section, position, Previous/Next, contextual Explain/Verify, and Exit. Advisor-only Briefing types use their internal generated sequence for an advisor Presentation and do not silently become client content. Exact attribution tables are preserved when the report's job is reconciliation.

## Explain / Verify

Explain starts from the current conclusion and uses the committed workflow question/purpose. Verify appears only for a rendered section with committed supporting HTML; it preserves exact report tables and the Briefing's fixed data date. Closing evidence returns to the same section and navigation position. Gated placeholders never receive a fake Verify action.

## Gated-step treatment

The committed workflow JSON controls status and visibility. The adapter supplies advisor-safe ordered-journey metadata and maps missing prerequisites to calm language covering data, method, approved report shape, or benchmark/proxy approval. Advisor Review may show the intended step in context. Client Preview and Presentation omit gated steps and empty report shells.

## Known demo limitations

- Synthetic Northstar Family Office data only; data date is 2026-06-30.
- Browser-local templates and Briefings are not production persistence.
- No production export/share, authentication, tenancy, privacy architecture, or audit lifecycle.
- No live market/custodian data or external APIs.
- No new scenario, valuation, attribution, proxy, benchmark, recommendation, or position-level calculations.
- Earlier full technical composer behavior is retained for Developer / QA compatibility, not as the ordinary advisor authoring path.

## Run locally

From the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn arangur.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/app/`. Docker is not required.

## Manual acceptance QA

Completed in a local headless Edge browser against the non-Docker FastAPI app on 2026-07-15:

1. Opened the Conversation Briefing Desk and confirmed the four catalog-driven Briefing types.
2. Opened Principal / Family Office Briefing and confirmed the ordered journey and calm advisor-plan gate.
3. Duplicated the built-in, changed the template name and material note, and saved a custom template.
4. Created a dated Briefing with the current synthetic snapshot and confirmed Advisor Review.
5. Confirmed Coverage and Confidence Warning appears in Advisor Review but not Client Preview.
6. Confirmed the gated advisor-plan step does not appear in Client Preview or Presentation.
7. Entered Presentation and passed Previous/Next navigation and Exit return behavior.
8. Returned to Advisor Review, opened Briefing history, and reopened the immutable Briefing.
9. Created a second Briefing from the same custom template and confirmed the first Briefing remained present.
10. Opened Advisor / Manager Oversight and confirmed the exact Manager Driver Attribution Matrix remains advisor/internal.
11. Opened External Manager Story Translation and confirmed all five governance statements and four gated analytic steps.
12. Opened Developer / QA and confirmed technical transfer/composer controls remain outside the ordinary journey.
13. Confirmed the ordinary home did not expose JSON, schema, workflow ID, artifact-path, or simulation-path language.
14. Confirmed no browser console or page errors.

Result: **pass**.
