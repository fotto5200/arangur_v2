# Briefing Templates and Generated Reports

The private-demo app at `/app/` uses one product lifecycle:

> Briefing template → generate with current data → generated report → open report

There is no separate conversation object or manifest navigation layer.

## Unified template model

`GET /api/briefing-templates` adapts the four committed definitions under `data/simulation/report_workflows/demo_workflows_v1/` into the same `arangur.local_briefing_spec_set.v1` payload used by browser-created workflows. Each built-in therefore has the ordinary ordered `client_briefing_set` and `advisor_review_set` lists, report element specs, workflow ID/name, target branch, and description.

Advisor Home shows these built-ins together with browser-created templates under **Briefing Templates**:

- Principal Briefing
- Engaged Client Review
- Advisor Oversight
- External Manager Story Translation

Every supported row can generate with current data, open in the existing builder, or be duplicated under a new custom name. Built-ins cannot be deleted or overwritten. Opening one for editing creates an unsaved working copy; duplicating one creates a normal browser-local custom template.

## Generated reports

**Generated Reports** is a separate list of dated artifacts. Direct generation calls the existing `POST /api/generated-reports/demo-populate` service with the selected template's ordinary payload, stores the returned artifact in the existing browser-local generated-report shelf, and opens the first actual rendered report immediately.

The presentation surface shows one report at a time with **Previous**, **Next**, and “Report N of M” navigation. Print and export continue to use the complete artifact. Gated catalog steps remain in sequence as restrained unavailable sections; no synthetic result is invented.

Existing custom workflows, narrative elements, report-element configuration, Save As New, generated-report storage, print/export, and Developer / QA tools remain in place. External Manager Story Translation retains its translation-not-endorsement, synthetic, unverified, non-recommendation, candidate-proxy approval, and pre-production-review boundaries.

## Restart and smoke test

From Windows `cmd`:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
docker compose --env-file .env.private-demo down
docker compose --env-file .env.private-demo up --build
```

In another `cmd` window:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_smoke.cmd
```

Open `http://127.0.0.1:8000/app/`, generate Principal Briefing, use Next/Previous, return to Briefings, reopen it under Generated Reports, and duplicate the built-in to confirm the original remains unchanged.

Stop with:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_down.cmd
```

This remains a synthetic, browser-local private demo. Deployment, authentication, durable generated-report persistence, live data, and production client use remain outside this tranche.
