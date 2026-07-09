# Report Workflow Catalog v1

A report workflow is an ordered conversation for a specific audience and use case. It is not every report the system can produce.

This catalog is local product structure only. It does not wire Advisor Home, Preview, Populate, Present, generated reports, backend endpoints, Docker, deployment, live data, external APIs, real data, or recommendations.

## Workflows

| Workflow | Audience | Detail level | Conversation goal |
| --- | --- | --- | --- |
| Principal / Family Office Briefing | Principal / family office member | minimal_client_briefing | Answer where we are, whether cash/spending is covered, what the biggest risks are, what to watch next, and what the advisor is planning to do. |
| Engaged Client / Investment Committee Review | Engaged client, family investment committee, or sophisticated principal | sophisticated_client_or_committee | Explain performance, exposures, themes, and risk without turning the meeting into advisor internal diligence. |
| Advisor / Manager Oversight | Advisor/internal investment team | advisor_internal_diagnostic | Monitor mandates, manager performance, implementation quality, drift, and review flags. |
| External Manager Story Translation | Advisor, investment committee, or manager-facing discussion | advisor_or_committee_translation | Translate an external investment narrative into Arangur structures without endorsing or verifying it. |

## Workflow Versus Report Family

A report family defines a reusable report type, such as Portfolio Representation Status or Advisor Policy Attribution. A workflow chooses a small ordered subset of report families for one meeting.

## Accepted Attribution Sequence

The accepted sequence is policy allocation setup, advisor policy attribution, manager mandate attribution, manager driver matrix when needed, selected-manager drill-down for advisor oversight, and handoff control only when reconciliation is the question.

Policy-Level Attribution Summary v1 is superseded as the primary product-review surface. Equal-weight AI Adoption Attribution remains diagnostic unless explicitly selected as policy.

## Setup Notes Versus Client-Facing Reports

Setup/readiness notes explain whether data, coverage, benchmark basis, or allocation basis is ready. They can support a workflow, but they should not be presented as the main client answer unless the meeting topic is readiness.

## External Manager Story Workflow

The external story workflow matters because an outside manager worldview often arrives as narrative. Arangur can translate that narrative into lenses, key-price scenarios, candidate proxies, and report-workflow gates without endorsing or verifying it.
