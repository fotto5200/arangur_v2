# Arangur Objective Horizon Manager Refinement v1

Status: Preferred concept under refinement; not frozen
Depends on: `arangur_ui_selected_direction_v1.md`
Scope: Portfolio and manager presentation inside the client-facing Plan Check

## Refinement objective

Extend Objective Horizon from the consolidated portfolio into manager explanation without turning the client report into a manager dashboard or a sequence of repetitive reports.

## Stable semantic direction

Every horizon uses a target or boundary at its center:

- favorable results extend right;
- unfavorable results extend left;
- color reinforces but never determines meaning;
- absolute actual and target values remain directly labeled;
- the bar length expresses distance from the applicable objective or boundary, not raw magnitude from zero.

This replaces the earlier downside rail in which a larger loss extended rightward.

## Information architecture

The manager experience is a contextual drill-down inside the portfolio briefing:

**Portfolio Horizon → Manager contribution horizon → Selected manager horizon → Evidence → Return to portfolio**

Individual manager reports remain available for manager-specific meetings, but the client is not forced through a separate generated report for every manager.

## State 1 — Portfolio Horizon

### Client question

Is the overall plan on track?

### Visible

- Return: 7.79% actual versus 6.5% design-only objective; +1.29 percentage points favorable.
- Net asset growth: 5.2% actual versus 4.0% design-only objective; +1.2 percentage points favorable.
- Resilience: -21.1% AI / Chip Selloff versus -15.0% design-only review boundary; 6.1 percentage points unfavorable.
- One conclusion: “Growth is ahead of plan. One risk is outside the review boundary.”
- Dominant action: **See manager contributions**.

### Hidden

Manager roster, attribution categories, scenario mechanics, holdings, and all setup controls.

## State 2 — Manager contribution horizon

### Client question

Which decisions and managers materially drove the portfolio result?

### Visible

- Net decision effect versus the global policy basis: +0.79 percentage points.
- Advisor policy/allocation effect: -0.26 percentage points.
- Combined manager implementation effect: +1.05 percentage points.
- Manager contribution rows ordered by consequence:
  - Manager A — Growth / AI Infrastructure: +0.52 percentage points.
  - Manager D — Private Markets / Real Assets: +0.16 percentage points.
  - Manager B — Core Quality Equity: +0.15 percentage points.
  - Manager F — Opportunistic Macro / Hedge: +0.13 percentage points.
  - Manager C — Income and Cash Generation: +0.05 percentage points; allocation review.
  - Manager E — Liquidity Reserve / Defensive Ballast: +0.04 percentage points.
- A single selected manager and dominant action: **Open manager horizon**.

### Visual rule

Aligned manager rows are used for comparison. A stacked bar may appear only as a compact explanation of additive contributions summing to +1.05 percentage points. Manager returns, mandate comparisons, and scenario percentages are never stacked because they do not share an additive denominator.

### Hidden

Mandate selection/sizing, asset selection/sizing, residuals, fully detailed benchmarks, and holdings.

## State 3 — Selected manager horizon

### Client question

Is this manager fulfilling its role, contributing to the portfolio, and positioned as intended?

### Visible objectives

1. **Mandate performance** — manager return relative to assigned mandate.
2. **Portfolio contribution** — weight-adjusted contribution to total portfolio result.
3. **Allocation-to-role** — whether the advisor’s allocation to the manager remains within its target tolerance.

The third objective explicitly belongs to the advisor’s allocation decision. It must not be presented as manager failure.

### Example: Manager A

- Actual return 11.6% versus 9.5% mandate: +2.10 percentage points favorable.
- Portfolio contribution: +0.52 percentage points.
- Actual weight 24.86% versus 22.0% target: +2.86 percentage-point drift, shown as within the design-only ±3.0 percentage-point tolerance by 0.14 percentage points.

### Example: Manager C

- Actual return 4.7% versus 4.3% mandate: +0.40 percentage points favorable.
- Portfolio contribution: +0.05 percentage points.
- Actual weight 13.02% versus 17.0% target: -3.98 percentage-point drift, shown as 0.98 percentage points outside the design-only ±3.0 percentage-point tolerance.
- Responsibility statement: “The manager exceeded its mandate; the allocation to the manager requires advisor review.”

### Dominant action

**Return to portfolio** after the manager conclusion is understood. Explain and Verify remain secondary paths attached to the visible claim.

## Comparison-basis rules

- Portfolio success is judged against client objectives.
- Manager performance is judged against the manager’s assigned mandate.
- Manager contribution is judged as a weight-adjusted effect on the portfolio.
- Allocation drift is an advisor decision unless the mandate assigns that responsibility elsewhere.
- Scenario contribution must use the same portfolio base and scenario as the consolidated result.
- A manager’s raw return is not compared directly with the total portfolio return by default.

## Shared reporting language versus report-specific freedom

Objective Horizon is a candidate for Arangur’s shared reporting language, not a mandate that every report use horizon bars.

### Elements intended to carry across reports

- conclusion before evidence;
- favorable-right and unfavorable-left semantic direction;
- direct actual, objective, and boundary labels;
- stable terminology for observed results, objectives, deterministic scenarios, and probability ranges;
- Understand → Explain → Verify depth;
- one conclusion and dominant action per presentation state;
- consistent scenario bases and scales;
- restrained, meaningful motion;
- client-facing content separated from analytical and setup machinery.

### Elements allowed to vary by report

- chart form: horizon, capital bridge, timeline, distribution, attribution, exposure composition, or number line;
- whether the report is organized around objective, time, causal contribution, or composition;
- density at the Explain and Verify levels;
- whether manager small multiples, a scenario range, or an exposure map best answers the question;
- presentation sequence appropriate to the report’s job.

## Breadth-before-depth gate

Before Objective Horizon becomes the global report style, its shared language must be tested on different report archetypes:

1. **Cash Support** — required versus generated cash, capital preservation, and evolution over time.
2. **Scenario Risk** — deterministic events and probabilistic ranges on consistent portfolio-value scales.
3. **Lens Alignment** — intended story, exposure composition, manager sources, and classification gaps.
4. **Advisor Attribution** — manager-by-manager allocation decisions on a portfolio-effect denominator.
5. **Manager Attribution** — benchmark-by-benchmark decision attribution within a selected manager on its own explicitly stated denominator.

Advisor Attribution and Manager Attribution are separate specimens. Their row meanings, denominators, totals, and decision responsibilities may not be merged merely because both are attribution reports. The test asks which rules transfer and which visual forms must remain report-specific. Only after that comparison should Arangur freeze a visual reporting system or deeply polish one report family.

## Design-only assumptions

The 6.5% return objective, 4.0% asset-growth objective, ±3.0 percentage-point allocation tolerance, and -15% downside boundary are illustrative. They are not supplied Northstar client facts.
