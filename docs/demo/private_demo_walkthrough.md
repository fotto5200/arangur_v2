# Private Demo Walkthrough And QA Checklist

This walkthrough uses synthetic demo data and browser-local template/report storage. It is not a public deployment or production reporting process. The unified template model is described in `docs/demo/advisor_report_workflows.md`.

## Start and smoke

From Windows `cmd`:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
docker compose --env-file .env.private-demo down
docker compose --env-file .env.private-demo up --build
```

In a second `cmd`:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_smoke.cmd
```

Open `http://127.0.0.1:8000/app/`.

## Built-in template flow

1. Confirm Advisor Home is titled **Briefings**.
2. Confirm **Briefing Templates** contains Principal Briefing, Engaged Client Review, Advisor Oversight, and External Manager Story Translation.
3. On Principal Briefing, choose **Generate with current data**.
4. Confirm the first actual report opens directly rather than a stage-card manifest.
5. Confirm the page shows **Report 1 of 7**, **Previous**, and **Next**.
6. Use Next to move through the report sequence.
7. Choose **Back to Briefings**.
8. Under **Generated Reports**, open the dated Principal Briefing again.
9. Confirm Print, Export HTML, and Copy text remain available.

## Duplicate and edit flow

1. Return to **Briefing Templates**.
2. Choose **Duplicate / Save as** on Principal Briefing.
3. Confirm a custom “Principal Briefing Copy” row appears and the built-in remains.
4. Choose **Open / edit** on the custom template.
5. Change a title, report element, narrative item, scenario, or ordering.
6. Save under a distinct name.
7. Return to Briefings and generate either version.
8. Confirm each generated report names the correct source template.

Existing browser-created workflows such as July 3rd Workflow should appear in the same Briefing Templates list and retain Open/edit, Duplicate/Save as, Generate, and safe Delete actions.

## QA checklist

### Home

- [ ] Briefing Templates and Generated Reports are the two primary sections.
- [ ] Built-in and custom templates share one list.
- [ ] No Choose a conversation section or separate journey navigation remains.
- [ ] Create/manage and Developer / QA tools are secondary and collapsed.

### Templates

- [ ] Built-ins use Generate with current data, Open/edit, and Duplicate/Save as.
- [ ] Built-ins cannot be deleted or overwritten.
- [ ] Duplicating creates a custom template with a new ID.
- [ ] Existing custom workflows still open, edit, generate, duplicate, and delete safely.
- [ ] Narrative/report element order survives duplicate and generation.

### Generated reports

- [ ] Direct generation opens report 1 immediately.
- [ ] Previous/Next navigation follows template order.
- [ ] Generated Reports lists report title, source template, generated time, and data-as-of date.
- [ ] Open report returns directly to actual report content.
- [ ] Gated sections use restrained unavailable language and do not invent results.
- [ ] Print, Export HTML, and Copy text remain available.

### Boundaries

- [ ] External Manager Story Translation remains synthetic, unverified, not a recommendation, and translation rather than endorsement.
- [ ] Candidate proxies still require approval and production client use requires review.
- [ ] No raw JSON, source paths, or debug metadata appears in the advisor path.
- [ ] No real client data, live market data, or external API is used.

## Stop

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_down.cmd
```

Current limitations remain browser-local generated-report storage, no durable backend report history, no production authentication, no public deployment, and synthetic data only. Do not commit `.env.private-demo`.
