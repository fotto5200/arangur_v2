# Advisor Report Workflows

The private-demo advisor app at `/app/` now opens with a report-journey chooser above the existing workflow design and management tools. It presents exactly four conversation paths: Principal Briefing, Engaged Client Review, Advisor Oversight, and External Manager Story Translation.

## Sources and serving

`GET /api/advisor-workflows` reads the four committed definitions in `data/simulation/report_workflows/demo_workflows_v1/` through the small adapter in `src/arangur/app/advisor_workflows.py`. The adapter preserves each definition's `ordered_steps` sequence while replacing internal catalog names with concise advisor-facing journey names and availability labels.

An available step receives a preview link only when its catalog entry identifies an existing, allowlisted mockup or external-story artifact. `GET /api/advisor-workflows/{workflow_id}/reports/{report_id}/preview` renders that committed Markdown or JSON content as a clean synthetic-demo page. It does not expose source paths, accept arbitrary paths, recalculate a report, or browse the artifact catalog.

Gated and deferred steps remain in conversation order with a short status and no link. An accepted step with missing preview content also remains visible without a broken link. If one workflow definition fails to load or validate, the chooser retains its four expected choices and uses restrained unavailable language for the affected journey.

The External Manager Story Translation page keeps its translation-not-endorsement, synthetic, unverified, non-recommendation, candidate-proxy approval, and pre-production review boundaries visible above the ordered stages.

## Restart and smoke test

From Windows `cmd`, restart the existing private-demo stack:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
docker compose --env-file .env.private-demo down
docker compose --env-file .env.private-demo up --build
```

In another `cmd` window, run the private-demo smoke:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_smoke.cmd
```

Then open `http://127.0.0.1:8000/app/`, select each journey, confirm the catalog order, open at least one available preview, and confirm gated steps have no preview action.

Stop the stack with:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_down.cmd
```

The later deployment tranche still owns private hosting and deployment validation. This tranche does not change Docker/Compose, authentication, environment keys, infrastructure, or deployment behavior.
