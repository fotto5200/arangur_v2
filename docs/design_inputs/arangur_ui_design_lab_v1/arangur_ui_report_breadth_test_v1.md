# Arangur Report Breadth Test v1

Status: Five compact report specimens refined after first cross-report review; no global visual system frozen
Depends on: `arangur_ui_objective_horizon_manager_refinement_v1.md`
Scope: One opening and one explanatory state per report

## Purpose

Test whether the emerging Arangur reporting language transfers across materially different analytical jobs without forcing every report into horizon bars.

## Shared language under test

- conclusion before construction or methodology;
- direct actual, objective, boundary, and as-of labels;
- favorable-right and unfavorable-left direction when direction is meaningful;
- common scales only when values share a valid base, unit, and interpretation;
- clear separation of observed result, deterministic scenario, and probability range;
- Understand → Explain → Verify depth;
- one dominant action per presentation state;
- tables retained when exact cross-row or cross-column comparison is the task;
- technical and administrative machinery hidden.

## Specimen 1 — Cash Support

### Opening question

Can the portfolio support the client’s required cash without unplanned principal erosion?

### Opening conclusion

> Next-period cash is projected to cover the $1.2M need by approximately $115K.

### Opening visual

Required cash and projected cash share one dollar scale. The cushion extends in the favorable direction. This is an appropriate use of an objective horizon because the values share a unit, horizon, and meaning.

### Explain state

A cash bridge shows $1.4M generated, $1.1M paid, and $255K retained/reinvested. The remaining rounding/reconciliation difference is disclosed at verification depth. The bridge is preferred over another horizon because the task becomes explaining how cash moved.

### Transfer test

Objective comparison and semantic direction transfer. The chart form changes from horizon to bridge when the question changes from status to composition.

## Specimen 2 — Scenario Resilience

### Opening question

What could knock the portfolio off course, and how large are the outcomes?

### Opening conclusion

> The AI / Chip Selloff crosses the review threshold; the Rate Shock does not.

### Opening visual

Current value, the directly named review threshold, and deterministic scenarios appear on a single $30M–$50M portfolio-value number line. A softly shaded review zone makes the threshold’s consequence explicit. AI / Chip Selloff, Rate Shock, current value, and the threshold each use a distinct, repeated color and a complete direct label. The common scale is valid because all marks use the same portfolio base and dollar unit.

### Explain state

Three aligned lanes reuse the same dollar axis while preserving different meanings:

- a deterministic result is a point produced by one specified event;
- a sensitivity interval shows how that result changes only when named severity inputs are deliberately varied;
- a probability range summarizes a modeled outcome distribution.

A deterministic result does not receive an “error bar.” If Arangur varies an event’s severity assumptions, the resulting interval is labeled a **sensitivity range**, never statistical uncertainty. Position-level before/after valuation remains at verification depth.

### Transfer test

Direct conclusions, boundaries, and stable scales transfer. Horizon bars do not; a number line is the natural visual form.

## Specimen 3 — Lens Alignment

### Opening question

Does the portfolio still express the AI Adoption story the advisor intended?

### Opening conclusion

> The portfolio has meaningful direct AI exposure, while 10.5% still requires classification review.

### Opening visual

A part-to-whole exposure bar shows the complete AI lens composition. Immediately below it, a color-keyed table defines every bucket and reports value, portfolio share, and position count. The same color identity connects even the smallest segment to its exact row. The review-required segment is directly identified; it is not converted into an arbitrary score.

### Explain state

Manager rows show how each manager contributes to the same lens buckets. This may use aligned composition bars or a compact matrix. The denominator—each manager’s own value—must remain visible because manager rows cannot be read as portfolio contributions without reweighting.

### Transfer test

Conclusion hierarchy, direct labels, and exception emphasis transfer. Semantic left/right direction does not apply to every exposure category, so composition retains stable categorical identity instead.

## Specimen 4 — Advisor Attribution

### Opening question

How did the advisor’s manager selection and allocation decisions affect the total portfolio?

### Denominator

Percentage points of total portfolio return on the stated global policy basis.

### Opening conclusion

> Advisor policy and allocation decisions detracted 0.26 percentage points; Manager C and Manager E were the largest negative rows.

### Opening visual

A true table is primary. Each manager is a row. Columns establish target and actual allocation, weight drift, mandate return, advisor policy effect, and status. The total row reconciles to -0.26 percentage points.

### Explain state

A compact additive bridge first summarizes selected-mandate, target-weighting, funding-drift, and total advisor-policy effects. The second table then decomposes those same effects by manager. The graphic is an orientation layer; the exact table remains primary because cross-row comparison and reconciliation are the job.

### Table contract

- manager rows plus a total calculated from unrounded effects; any displayed rounding difference is disclosed;
- one portfolio-effect denominator stated above the table;
- units included in headers;
- direct signs and aligned decimals;
- status used only for material review conditions;
- negative color may reinforce signs but never replace them;
- definitions and formulas on demand rather than permanent paragraphs.

## Specimen 5 — Manager Attribution

### Opening question

Within one selected manager, which benchmark and security decisions added or detracted from value?

### Denominator

Percentage points of the selected manager’s active return in the design specimen. Portfolio contribution is shown separately and is not mixed into the table total.

### Opening conclusion

> Manager A added 2.10 percentage points versus its mandate; Core AI Hardware decisions produced the largest contribution.

### Opening visual

A true table is primary. Each assigned benchmark or decision sleeve is a row. The table shows benchmark weight, active return, and total effect on the manager’s result.

### Explain state

A compact additive bridge first shows which decision family drove the manager’s result. The expanded table then decomposes each benchmark row into benchmark selection, benchmark sizing, security selection, and security sizing. Row and column totals reconcile to the manager’s +2.10 percentage-point active result. The bridge never replaces the audit table.

### Table contract

- benchmark or decision-sleeve rows, never manager rows;
- selected-manager denominator stated above the table;
- portfolio contribution reported outside the additive manager-return total;
- grouped headers separate benchmark decisions from security decisions;
- row totals and column totals both reconcile at the stored precision;
- negative effects remain signed and visually quiet until material;
- exact values remain visible because auditability is the job.

### Design-only fixture

The within-manager benchmark rows and effects are illustrative because the supplied screenshots do not include a benchmark-level Manager A table. They exist to test layout and arithmetic, not to assert actual Northstar results.

## Breadth-test decision criteria

After reviewing all five specimens, classify each rule as:

1. **System-wide** — should appear across client reports.
2. **Report-family** — appropriate only to objective, scenario, composition, or attribution reports.
3. **Specimen-specific** — useful for this report and not inherited elsewhere.

No visual system should be frozen until the attribution tables remain genuinely usable and the scenario and lens reports remain honest without horizon bars.
