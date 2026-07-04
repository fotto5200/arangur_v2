# Analytic Report Demo Story v1

This local demo shows how Arranger-published analytic choices become simple advisor-facing report content.

Arranger defines approved themes, scenarios, lenses, and confidence language in the demo analytic pack. The Advisor App exposes only curated choices from that pack. The advisor chooses report elements and labels; the synthetic Northstar portfolio is analyzed through the committed local proof outputs; Preview, Populate, and Present then show readable report fragments.

The goal is not to show every number. The goal is to support a client/advisor conversation about what deserves attention.

## Human Story

- Hidden concentration: approved themes reveal overlap that is not obvious from manager names alone.
- Manager overlap: manager rows show where nominal diversification may share the same themes.
- Scenario impact: the AI / Chip Selloff view shows which managers and themes carry the visible stress.
- Data confidence: the report separates high-confidence support from proxy and review-required inputs.
- Resilience: the portfolio status and scenario views call out repeated vulnerabilities and relative ballast across the synthetic scenario set.

The advisor should not see control-plane tools, raw analytic JSON, shock construction, taxonomy setup, or internal model-building fields.

## Recommended Client Briefing Sequence

1. Portfolio Status / Resilience Snapshot
2. Theme Concentration / Hidden Overlap
3. Scenario Impact by Manager and Theme
4. Data Confidence Note
5. Advisor-added discussion prompt or short narrative element if desired

## Recommended Advisor Review Sequence

1. Manager Comparison / Overlap
2. Data Confidence / Opaque Exposure
3. Scenario Vulnerability
4. Cross-Scenario Resilience
5. Internal follow-up notes if the advisor adds them

## Canonical Local Workflow

Use `docs/demo/analytic_demo_workflow_fixture.json` as the canonical browser-local workflow fixture. Restore it from Developer / QA tools with `Restore local workflow JSON`, then Preview, Populate, and Present it with `Current synthetic demo snapshot`.

Expected behavior:

- supported analytic elements resolve to analytic-derived rendered fragments;
- generated reports preserve the restored workflow order;
- selected labels such as `AI Infrastructure`, `AI / Chip Selloff`, and `Human Review Required` appear in the report;
- unsupported scenario choices remain clean placeholders if the workflow is edited to use one.

This remains local/private-demo only. It uses synthetic demo data, browser-local workflow storage, and browser-local generated report shelf records.
