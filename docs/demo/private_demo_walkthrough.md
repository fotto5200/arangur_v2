# Private Demo Walkthrough And QA Checklist

This walkthrough is for a local private-demo operator. It uses only synthetic demo data and the browser-local workflow/report path. It is not a public deployment runbook and is not a production reporting process.

Manual checkpoint: Frank passed this local private-demo browser rehearsal after commit `524a99b` on 2026-07-03. The copied-workflow Populate path used the correct selected workflow, generated reports preserved the authored workflow sequence, automatic framing/closing sections were not inserted, and Present / view reports opened the generated report. For a clean rehearsal, clear old local generated reports from Developer / QA tools if prior shelf records make testing hard to read.

## Start The Stack

From Windows cmd at the repo root:

```cmd
copy .env.private-demo.example .env.private-demo
docker compose --env-file .env.private-demo up --build
```

If Docker reports that the daemon or Linux engine is unavailable, start Docker Desktop, wait for the Linux engine, and rerun the Compose command. If port `8000` is already in use, stop the other local service before starting this stack.

## Run Smoke Checks

In a second Windows cmd:

```cmd
scripts\private_demo_smoke.cmd
```

The smoke script checks health, the app shell, the report-element catalog, and synthetic briefing spec-set save/list paths. It does not require Docker in unit tests and does not use real client data.

## Open The App

Open:

```text
http://127.0.0.1:8000/app/
```

Or from cmd:

```cmd
start "" http://127.0.0.1:8000/app/
```

## Product Click-Through

1. Start at Advisor Home.
2. Choose `Create a new workflow`.
3. Create a `Client Briefing Workflow`.
4. Give the workflow a readable name with spaces.
5. Add a small sequence of report elements and narrative sections.
   - For an analytic-content rehearsal, include one approved-pack element such as Concentration with `Strategic Theme` / `AI Infrastructure`, Manager Comparison with `Strategic Theme`, Scenario Impact by Manager with `AI / Chip Selloff`, or Data Confidence Note with `Data Confidence`.
6. Save the workflow.
7. Return to Advisor Home.
8. Choose `Populate a workflow with data`.
9. Select the saved workflow and use `Current synthetic demo snapshot`.
10. Confirm `Source workflow` shows the workflow you selected.
11. Choose `Create demo populated report`.
12. Confirm the generated report opens.
13. Return Home.
14. Choose `Present / view reports`.
15. Open the generated report from the local report shelf.
16. Confirm `Print`, `Export HTML`, and `Copy text` are present.
17. Optional: create an `Advisor Review Workflow` and repeat the same abbreviated Populate and Present path.

## Stop The Stack

```cmd
scripts\private_demo_down.cmd
```

Or:

```cmd
docker compose --env-file .env.private-demo down
```

Use `scripts\private_demo_down.cmd --reset` only when you intentionally want to remove the local Postgres demo volume.

## QA Checklist

Mark each item pass/fail during the local demo rehearsal.

### Infrastructure

- [ ] Docker stack starts.
- [ ] `http://127.0.0.1:8000/api/health` returns OK.
- [ ] `http://127.0.0.1:8000/app/` loads.
- [ ] `scripts\private_demo_smoke.cmd` passes.

### Home And Workflow

- [ ] Advisor Home has exactly four top-level product choices.
- [ ] Developer / QA tools are secondary.
- [ ] Create workflow path works.
- [ ] Work with existing workflow path works.

### Builder

- [ ] Readable workflow names preserve spaces.
- [ ] Save, open, copy, and delete are understandable.
- [ ] Builder does not feel like a technical console.
- [ ] Scope choices do not imply unsupported previews.
- [ ] Approved analytic choices appear as curated themes, scenarios, lenses, and confidence focus labels, not control-plane construction fields.

### Populate

- [ ] Saved workflow can be selected.
- [ ] Source workflow confirmation matches the selected saved workflow.
- [ ] Current synthetic demo snapshot is clear.
- [ ] Demo populated report is created.
- [ ] Generated report opens.

### Present

- [ ] Generated report appears in `Present / view reports`.
- [ ] Opening it shows the report, not Builder.
- [ ] Print, Export HTML, and Copy text controls are visible.
- [ ] No raw JSON or debug metadata appears in the advisor path.

### Content

- [ ] Generated report body follows the saved workflow sequence.
- [ ] Advisor-authored narrative titles/text appear exactly where added.
- [ ] Selected report element titles are not replaced by alternate generated-report titles.
- [ ] Caveats are restrained.
- [ ] Unsupported sections use nontechnical language.
- [ ] Supported analytic elements render analytic-derived content in Preview and the populated report; unsupported scenario choices remain clean placeholders.

## Current Limitations

- Synthetic demo data only.
- Browser-local generated report shelf only.
- No production report history.
- No durable backend generated report persistence.
- No production authentication.
- No public deployment.
- No real client data.
- No live Plaid or market data.
- Do not commit `.env.private-demo`.
