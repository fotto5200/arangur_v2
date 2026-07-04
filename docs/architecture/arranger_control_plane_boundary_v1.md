# Arranger Control Plane Boundary v1

## Purpose

This document defines the boundary between the internal Arranger analytic control plane and the advisor-facing Arangur app.

The product direction is publish/consume:

- Arranger Internal Analytic Studio / Control Plane publishes approved analytic packs.
- Calculation and application code applies those approved packs to portfolio data.
- Arangur Advisor App consumes the approved packs and lets advisors select curated choices while building workflows and reports.

The control plane is internal Arranger capability. It is not advisor-facing UI, not a third Advisor Home menu item, and not a new public product surface inside Arangur.

## A. Arranger Internal Analytic Studio / Control Plane

The control plane is where Arranger defines, reviews, versions, and approves analytic choices before they are published as product artifacts.

Internal control-plane responsibilities include:

- Theme catalogs, such as AI Infrastructure, Rate Sensitivity, Private Market Liquidity, and Energy Security.
- Classification lens catalogs, such as theme, asset class, manager role / mandate, liquidity bucket, and data confidence.
- Scenario catalogs, including advisor-readable scenario names, supported horizons, driver narratives, caveats, and supported report elements.
- Scenario market-state construction policies, including approved key-rate/driver perturbations, expansion rules, qualitative assumptions, confidence labels, and caveats.
- Covariance, factor, and key-rate assumptions later, only as internal inputs for constructing coherent scenario market states.
- Data confidence rules that explain when data is high, medium, low, unknown, stale, proxy-based, or human-review required.
- Report analytic capability maps that say which report elements can consume which themes, lenses, scenarios, scopes, and inputs.
- Approved analytic pack manifests that bind component versions into a publishable pack.

Control-plane outputs are approved analytic packs. They are product artifacts with ids, versions, authorship, approval metadata, component paths, caveats, and compatibility expectations.

Advisors should not define covariance matrices, key-rate scenarios, scenario shock vectors, theme taxonomies, classification rules, or analytic model assumptions in Arangur. Advisors select from approved choices.

## B. Calculation / Application Layer

The calculation/application layer applies approved analytic packs to a specific portfolio and data snapshot.

Application responsibilities include:

- Theme exposure calculations using approved theme definitions and position classifications.
- Manager overlap views using approved manager-role and theme/lens definitions.
- Scenario impact calculations by full portfolio revaluation: value every position under the base market state, value every position under the approved scenario market state, and calculate impact as scenario value minus base value.
- Post-valuation attribution of impacts by position, manager, account, sleeve, theme, scenario, and confidence bucket.
- Data confidence summaries using approved confidence rules.
- Cross-scenario resilience views using approved scenario sets and capability maps.

This layer can be implemented locally for the demo and can use internal cloud compute later. Using cloud compute internally does not make the control plane part of the advisor app.

The application layer should treat analytic packs as read-only published inputs. It may validate compatibility, apply pack components, and return portfolio-specific outputs, but it should not mutate or invent approved pack definitions.

## C. Arangur Advisor App

The Arangur Advisor App is the advisor/client-facing workflow and reporting surface.

Advisor-app responsibilities include:

- Consuming approved analytic packs.
- Letting advisors choose from published scenarios, themes, lenses, scopes, and report elements.
- Building saved workflows and generated report artifacts.
- Presenting populated reports using advisor-authored workflow order and approved analytic outputs.

The advisor app does not expose control-plane construction tools. It should not include an Arranger Studio panel, taxonomy editor, shock-vector editor, covariance editor, or model-assumption editor.

## Product Boundary

Approved analytic packs are the handoff between Arranger and Arangur:

- Arranger publishes the pack.
- Arangur consumes the pack.
- Advisors select from the pack.
- Portfolio-specific calculation applies the pack.
- Generated reports present results and caveats.

This boundary keeps product behavior simple. It lets Arranger improve analytic content internally without turning the advisor app into an analytic-model-building console.

## Current Demo Proof

The current repo includes a synthetic proof of this boundary:

- `data/analytic_packs/arranger_demo_pack_v1/` is the approved pack fixture.
- `src/arangur/analytics/analytic_pack_loader.py` loads and validates that pack.
- `src/arangur/analytics/apply_demo_pack.py` applies the pack to existing synthetic portfolio, scenario, and valuation fixtures.
- `data/simulation/analytics/` stores deterministic proof outputs for theme exposure, manager/theme overlap, scenario impact by manager/theme, data confidence, and cross-scenario resilience.
- `src/arangur/report_elements/analytic_input_mapping.py` maps those proof outputs into separate analytic report-element input payloads.
- `src/arangur/report_elements/rendering.py` renders those analytic payloads into view JSON plus Markdown/HTML fragments for the current supported report elements.
- `src/arangur/report_elements/analytic_view_matching.py`, the static Advisor app, and the demo Populate service now consume those approved choices and fragments for supported workflow specs.

These proof outputs and fragments remain synthetic/local analytic artifacts. They are now consumed by the existing local Advisor workflow path, but the control-plane construction machinery remains internal and is not exposed as advisor-facing UI.

The controlling scenario methodology going forward is full portfolio revaluation under complete market states. Existing synthetic proof outputs should be treated as local artifacts to be realigned behind a full revaluation scenario-engine skeleton before additional advisor-facing analytics work expands.

## Deliberately Out Of Scope For This Boundary

- Advisor-facing control-plane UI.
- Arranger Studio UI implementation.
- Backend endpoints for analytic pack management.
- Scenario math, covariance engines, PCA, key-rate engines, or live market-data integration.
- Docker, deployment, AWS, Lightsail, Caddy, Cloudflare, DNS, or production-auth changes.
- Real client data or external API calls.
