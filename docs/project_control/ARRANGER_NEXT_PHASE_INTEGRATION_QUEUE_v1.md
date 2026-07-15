# Arranger Next-Phase Integration Queue v1

Status: recommended action sequence after documentation/UI discovery, 2026-07-15

Canonical naming note: the product name is **Arangur**. This historical `ARRANGER_...` filename is retained for path stability.

Blueprint status update, 2026-07-15: the Advisor Workflow UI Integration Blueprint v1 draft and companion contracts have been created. Frank review is now the exit gate; UI wiring must not begin until the blocking decisions in `docs/project_control/ARANGUR_UI_BLUEPRINT_FRANK_REVIEW_ITEMS_v1.md` are approved or revised.

## 1. Immediate next tranche

### Advisor Workflow UI Integration Blueprint v1

Purpose: integrate the committed workflow catalog, accepted report-family status, current advisor app, and external UI design-lab inputs into one repo-canonical UI blueprint before implementation.

Expected outputs:

- an approved product vocabulary and object lifecycle;
- a selected or explicitly deferred application interaction architecture;
- first-screen/workflow chooser contract;
- advisor builder/review/client preview/presentation boundaries;
- canonical ordered flows for all four workflow families;
- gated/deferred/error/readiness behavior;
- evidence and Developer / QA boundaries;
- a screen/state interaction contract suitable for implementation and tests;
- a list of design-lab ideas accepted, rejected, or deferred.

Exit gate: Frank approves the blueprint decisions. Do not treat an unselected lab direction as implicit authorization.

Created draft: `docs/product/advisor_workflow_ui_integration_blueprint_v1.md`, with application architecture, vocabulary/lifecycle, state-map, visibility/gating, machine-summary, and Frank-review companions.

## 2. Inputs needed

The blueprint should read and reconcile:

- `data/simulation/report_workflows/demo_workflows_v1/report_workflow_catalog_manifest.json` and the four workflow JSON files;
- `docs/product/report_workflow_catalog_v1.md`;
- `docs/product/report_family_acceptance_status_v1.md`;
- `docs/product/demo_report_suite_v1.md`;
- this project-control dossier, decision register, inventory, and UI digest;
- existing advisor app files, especially `src/arangur/app/static/index.html`, generated-report service/model contracts, and focused UI tests;
- repo-canonical UI/reporting docs under `docs/ui_reporting/`;
- accepted report mockups under `docs/product/report_mockups/`;
- external story translation pack under `data/simulation/external_story_translation/`;
- active design-lab Markdown and HTML inputs;
- current deployment-readiness and private-demo walkthrough docs for constraints only, not deployment action.

## 3. Blueprint decisions to make

### First screen / workflow chooser

- Decide whether entry is job/conversation-first, briefing-first, guide-first, or library/object-first.
- Map the four canonical workflow families into business-language choices.
- Decide whether “workflow” is visible terminology or an internal model.
- Keep one dominant action and hide raw artifact/report-library machinery.

### Workflow builder versus presenter

- Define builder power: select/reorder reports, add narrative, set visibility, review gates, and create/reuse templates.
- Define presenter simplicity: immutable dated briefing, Next, Explain, Evidence, and exact return to context.
- Separate authoring, generation/population, advisor review, client preview, and historical reading states.

### Client preview versus advisor review

- Specify which report steps are client-facing, advisor-review, advisor-only, setup/readiness, internal-control, or gated.
- Decide how optional dense reports such as Manager Driver Attribution Matrix appear.
- Place material caveats next to affected claims and move methodology/admin detail deeper.

### Custom workflow creation scope

- Decide whether v1 supports editing ordered reports in an approved template, creating a reusable template, or both.
- Define minimum fields: purpose, audience, ordered report/narrative elements, emphasis, exclusions, visibility, and data/readiness gates.
- Avoid exposing schema, raw IDs, renderer settings, or universal metric/lens combinatorics.

### Report display

- Choose compact ordered rows/agenda versus document outline versus guided steps based on the selected architecture.
- Use client-readable titles, questions answered, visibility, and readiness—not source paths or filenames.
- Open exact tables only when cross-row comparison/reconciliation is the job; otherwise lead with conclusion and minimal evidence.

### Gated/deferred items

- Show unavailable/gated reports calmly with reason categories: missing data, missing approved method, missing benchmark/proxy, or awaiting advisor approval.
- Do not create client-facing readiness reports as substitutes.
- Keep gated steps visible only when they help the advisor understand workflow completeness.

### External story caveats

- Mark the story as translated, not verified, not endorsed, and not a recommendation.
- Keep candidate proxies internal and approval-required.
- Do not enable portfolio-through-lens or scenario reports until the corresponding report shape, inputs, and approvals exist.

### Hide raw artifact names

- Replace mockup filenames, JSON filenames, artifact paths, workflow IDs, and run IDs with business titles.
- Keep source/evidence references available in an evidence or Developer / QA layer.

### What not to build yet

- Do not add analytics-control-plane construction tools to the advisor UI.
- Do not add production history/persistence merely to make a prototype feel complete.
- Do not add live data, real holdings, investment recommendations, or deployment work.

## 4. Implementation tranche after blueprint

### Advisor Workflow UI Wiring v1

Purpose: implement the approved blueprint against the current dependency-free advisor app and committed synthetic artifacts.

Bounded scope should include:

- canonical workflow chooser/entry;
- ordered workflow/template display;
- supported create/reuse/edit path;
- advisor review versus client preview/presentation;
- accepted/gated/deferred visibility rules;
- external story caveats;
- business-language titles and hidden artifact identifiers;
- focused UI/static tests and a local browser rehearsal.

It should not change analytics calculations, generate new report math, alter deployment configuration, or use real data.

## 5. Later tranches

1. **Local Docker demo polish** — rehearse the approved workflow end to end, resolve only observed blockers, and update the private-demo checklist.
2. **Fresh deployment thread** — restart with deployment-specific context and current security/readiness evidence.
3. **Private demo deployment** — only after host/auth/privacy decisions and explicit authorization.
4. **Internal analytics control-plane design** — define users, approval/version workflow, pack publishing, audit, and separation from advisor consumption.
5. **Private data execution architecture** — define client-data locality, minimization, encryption, tenancy, entitlements, retention, and audit before live holdings.
6. **Durable briefing/report history** — define immutable generated briefing storage and template lineage after the UI object model is approved.

## 6. Do-not-build-yet list

- Position-level drill-down.
- Full Manager-by-Manager Driver Detail with Position Drilldown.
- Internal analytics studio/control-plane UI.
- Real Plaid or custodian integration.
- AWS/Lightsail/Cloudflare/DNS deployment work.
- Production pricing or market-data integration.
- New scenario math or probabilistic ranges.
- Blended/all-in attribution.
- Timing attribution or dollar P&L attribution.
- Production/client attribution claims.
- Current-versus-proposed portfolio analytics.
- Production recommendation or autonomous advisor actions.

## Queue summary

| Order | Tranche | Outcome | Gate before next |
| --- | --- | --- | --- |
| 1 | Advisor Workflow UI Integration Blueprint v1 | Canonical product/UI contract | Frank approval of unresolved decisions |
| 2 | Advisor Workflow UI Wiring v1 | Working local synthetic workflow UI | Focused tests and browser rehearsal pass |
| 3 | Local Docker demo polish | Accepted local private-demo journey | Explicit deployment readiness decision |
| 4 | Fresh deployment thread | Current scoped deployment plan | Explicit infrastructure/security authorization |
| 5 | Private demo deployment | Protected private demo | Separate operational acceptance |
