# Arranger Demo Analytic Pack v1

This directory contains the first meaningful synthetic Arranger analytic pack fixture.

It is a published-pack example for the Arranger control-plane boundary:

- Arranger defines approved themes, lenses, scenarios, shock assumptions, confidence rules, and report capability mappings.
- Arangur consumes the approved pack.
- Advisors later select from curated pack choices; they do not define the control-plane machinery.

## Contents

- `pack_manifest.json`
- `theme_catalog.json`
- `classification_lens_catalog.json`
- `scenario_catalog.json`
- `scenario_shock_pack.json`
- `data_confidence_rule_catalog.json`
- `report_analytic_capability_map.json`

## Regenerate Proof Outputs

From the repo root:

```cmd
set PYTHONPATH=src
python -m arangur.analytics.apply_demo_pack
```

This writes deterministic synthetic outputs under `data/simulation/analytics/`.

## Not Implemented

This pack does not add advisor UI, Arranger Studio UI, backend endpoints, report-element input mapping, generated-report wiring, scenario math, covariance/PCA/key-rate engines, live data, external APIs, real client data, deployment config, or dependencies.
