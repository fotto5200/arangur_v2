# Thesis Lens Position Mapping Design v1

## 1. Purpose And Boundary

This document defines how Arranger creates complete thesis-specific position mapping schemas.

A thesis lens is an internal Arranger-published artifact. It gives a portfolio a complete classification worldview for one advisor thesis, such as AI adoption, deglobalization, geopolitical bloc fragmentation, energy security, private liquidity stress, inflation persistence, or credit stress.

The Arangur Advisor App consumes approved thesis lenses and approved position mapping outputs. Advisors may select an approved thesis lens, scope, and report element, but they do not create taxonomy systems, categories, covariance assumptions, valuation machinery, or scenario-basis models live inside the advisor app.

Thesis lenses classify values and impacts after valuation:

```text
base_market_state
-> value every position
-> base_position_values

scenario_market_state
-> value every position
-> scenario_position_values

impact = scenario_position_value - base_position_value

approved_thesis_lens
-> map each position to one primary thesis bucket
-> aggregate already-valued base value, scenario value, and impact by bucket
```

Thesis lenses do not price positions, create scenario impacts, replace full revaluation, or substitute for position-to-market-input coverage mapping. They are a post-valuation attribution and explanation layer.

`docs/architecture/position_valuation_coverage_mapping_design_v1.md` defines the separate layer that decides how positions map to instruments, pricing functions, required market inputs, valuation results, and caveats before thesis-bucket aggregation begins.

## 2. Core Concepts

### A. Thesis Lens

A complete classification worldview for a particular advisor thesis. Examples include AI Adoption, Deglobalization / Isolationism, Cold War / Geopolitical Bloc, Energy Security, Credit Stress, and Private Liquidity Stress.

A thesis lens contains stable lens metadata, approved primary buckets, optional secondary flags, inclusion and exclusion rules, neutral and review buckets, versioning, and an assignment policy.

### B. Thesis Bucket

One mutually exclusive primary category inside a thesis lens. In v1, every in-scope position must be assigned to exactly one primary bucket for each selected thesis lens.

Primary buckets must support clean add-up logic. If a report says "Under the AI Adoption lens, 24% of scenario impact sits in Data Center / Power Bottleneck Exposure," that bucket total should be the sum of positions whose single primary assignment is that bucket.

### C. Secondary Flag

An optional non-additive label that preserves nuance without breaking primary bucket add-up logic.

Secondary flags can identify cross-cutting conditions such as China/Taiwan supply-chain exposure, regulatory sensitivity, hardware cycle sensitivity, private-market opacity, or power demand sensitivity. They are not weighted splits and do not sum to 100%.

### D. Position Thesis Assignment

The published mapping of one position to one primary bucket under one thesis lens.

Each assignment ties together:

- one `position_id`;
- one `lens_id`;
- one `lens_version`;
- exactly one `primary_bucket_id`;
- zero or more `secondary_flag_ids`;
- assignment method, confidence, rationale, review status, and source metadata.

### E. Thesis Mapping Schema

The complete versioned schema for one thesis lens. It includes lens metadata, buckets, bucket definitions, inclusion/exclusion rules, neutral and review buckets, secondary flag definitions, validation rules, assignment policy, and publication metadata.

### F. Position Evidence Packet

The internal evidence used to classify a position under a thesis lens. Evidence packets gather available identifier, issuer, sector, geography, security, manager, sleeve, mandate, look-through, business description, and source-quality data before classification.

Evidence packets are internal Arranger inputs. The advisor-facing app should not expose raw evidence packets by default.

## 3. Completeness And Orthogonality Rules

V1 uses the primary-bucket model:

- Every position in the selected scope maps to exactly one primary bucket per thesis lens.
- Primary buckets inside a lens are mutually exclusive.
- Primary buckets collectively cover the selected scope.
- Each lens must include a neutral or low direct exposure bucket.
- Each lens must include an unclassified or review required bucket.
- Secondary flags may be many-to-one and do not add to 100%.
- Weighted allocation is out of scope in v1 unless Frank explicitly approves it later.

Why this rule exists:

- Add-up logic must remain simple enough for reports to explain.
- Bucket totals should reconcile cleanly to the selected portfolio scope.
- Pseudo-precision should be avoided when classification evidence is incomplete.
- Client-facing reports need stable bucket totals, not fragile fractional taxonomy math.
- Ambiguity should route to review or secondary flags instead of forced weighted splits.

This differs from broader theme tagging. A position may have many general themes, but under one thesis lens it has exactly one primary bucket for additive attribution.

## 4. Example Thesis Lenses

The examples below define design-level lens schemas only. They are not production taxonomy approvals and do not create generated analytics outputs.

### A. AI Adoption Lens

Purpose: classify how a portfolio is exposed to the economic adoption, infrastructure buildout, disruption, and bottlenecks around AI.

Possible primary buckets:

- `core_ai_infrastructure_hardware`: Core AI Infrastructure / Hardware
- `ai_model_platform_exposure`: AI Model / Platform Exposure
- `ai_downstream_productivity_beneficiary`: AI Downstream Productivity Beneficiary
- `ai_disrupted_incumbent`: AI-Disrupted Incumbent
- `data_center_power_bottleneck_exposure`: Data Center / Power Bottleneck Exposure
- `neutral_low_direct_ai_exposure`: Neutral / Low Direct AI Exposure
- `unclassified_review_required`: Unclassified / Review Required

Possible secondary flags:

- `china_taiwan_supply_chain_exposure`: China/Taiwan supply-chain exposure
- `power_demand_sensitivity`: Power demand sensitivity
- `regulatory_sensitivity`: Regulatory sensitivity
- `private_market_opacity`: Private-market opacity
- `hardware_cycle_sensitivity`: Hardware cycle sensitivity

### B. Deglobalization / Isolationism Lens

Purpose: classify how a portfolio is exposed to trade fragmentation, domestic reshoring, import cost pressure, export demand sensitivity, and logistics disruption.

Possible primary buckets:

- `domestic_supply_chain_beneficiary`: Domestic Supply-Chain Beneficiary
- `cross_border_supply_chain_risk`: Cross-Border Supply-Chain Risk
- `shipping_logistics_sensitive`: Shipping / Logistics Sensitive
- `import_cost_sensitive`: Import-Cost Sensitive
- `export_demand_sensitive`: Export-Demand Sensitive
- `geopolitical_safe_haven_exposure`: Geopolitical Safe-Haven Exposure
- `neutral_low_direct_exposure`: Neutral / Low Direct Exposure
- `unclassified_review_required`: Unclassified / Review Required

Possible secondary flags:

- `tariff_sensitivity`: Tariff sensitivity
- `single_country_supply_dependency`: Single-country supply dependency
- `onshoring_beneficiary`: Onshoring beneficiary
- `currency_translation_sensitivity`: Currency translation sensitivity
- `logistics_bottleneck_exposure`: Logistics bottleneck exposure

### C. Cold War / Geopolitical Bloc Lens

Purpose: classify how a portfolio is exposed to bloc fragmentation, defense/security demand, strategic geography, commodity security, and geopolitical vulnerability.

Possible primary buckets:

- `us_bloc_beneficiary`: US Bloc Beneficiary
- `china_taiwan_exposure`: China/Taiwan Exposure
- `europe_strategic_exposure`: Europe Strategic Exposure
- `global_south_vulnerability`: Global South Vulnerability
- `defense_security_beneficiary`: Defense / Security Beneficiary
- `commodity_security_exposure`: Commodity Security Exposure
- `neutral_low_direct_exposure`: Neutral / Low Direct Exposure
- `unclassified_review_required`: Unclassified / Review Required

Possible secondary flags:

- `sanctions_export_control_sensitivity`: Sanctions / export-control sensitivity
- `semiconductor_supply_chain_exposure`: Semiconductor supply-chain exposure
- `strategic_minerals_exposure`: Strategic minerals exposure
- `defense_procurement_sensitivity`: Defense procurement sensitivity
- `jurisdictional_rule_of_law_sensitivity`: Jurisdictional rule-of-law sensitivity

### D. Energy Security Lens

Purpose: classify exposure to power reliability, energy supply, commodity availability, grid infrastructure, and transition bottlenecks.

Possible primary buckets:

- `energy_supply_beneficiary`: Energy Supply Beneficiary
- `grid_infrastructure_beneficiary`: Grid Infrastructure Beneficiary
- `energy_input_cost_sensitive`: Energy Input-Cost Sensitive
- `transition_policy_sensitive`: Transition Policy Sensitive
- `commodity_supply_security_exposure`: Commodity Supply Security Exposure
- `neutral_low_direct_energy_exposure`: Neutral / Low Direct Energy Exposure
- `unclassified_review_required`: Unclassified / Review Required

### E. Credit Stress Lens

Purpose: classify exposure to refinancing pressure, credit spread widening, default sensitivity, cash-flow resilience, and financial-system stress.

Possible primary buckets:

- `direct_credit_spread_sensitive`: Direct Credit Spread Sensitive
- `refinancing_wall_exposure`: Refinancing Wall Exposure
- `levered_cash_flow_sensitive`: Levered Cash-Flow Sensitive
- `financial_intermediary_exposure`: Financial Intermediary Exposure
- `cash_or_high_quality_defensive`: Cash Or High-Quality Defensive
- `neutral_low_direct_credit_exposure`: Neutral / Low Direct Credit Exposure
- `unclassified_review_required`: Unclassified / Review Required

### F. Private Liquidity Lens

Purpose: classify exposure to private-market marks, redemption constraints, financing constraints, exit-market sensitivity, and opaque holdings.

Possible primary buckets:

- `illiquid_private_mark_exposure`: Illiquid Private Mark Exposure
- `redemption_or_gate_sensitive`: Redemption Or Gate Sensitive
- `funding_liquidity_sensitive`: Funding Liquidity Sensitive
- `exit_market_sensitive`: Exit-Market Sensitive
- `liquid_defensive_exposure`: Liquid Defensive Exposure
- `neutral_low_direct_private_liquidity_exposure`: Neutral / Low Direct Private Liquidity Exposure
- `unclassified_review_required`: Unclassified / Review Required

## 5. Position Evidence Packet

A position evidence packet should be built before classification. It should include available data, source quality, and explicit missing fields.

Suggested fields:

- `position_id`
- `instrument_id`
- `ticker`
- `issuer`
- `company_name`
- `security_type`
- `asset_class`
- `sector`
- `industry`
- `geography`
- `currency`
- `manager`
- `sleeve`
- `mandate`
- `account`
- `holdings_lookthrough`
- `business_description`
- `revenue_segments`
- `supply_chain_geography`
- `fund_manager_description`
- `valuation_coverage_status`
- `data_freshness`
- `existing_tags`
- `human_notes`
- `source_metadata`
- `missing_evidence_fields`

Evidence packets should be internal Arranger inputs. They may contain raw descriptions, source notes, incomplete look-through records, or classification rationale that should not be shown in the main advisor-facing app by default.

## 6. Classification Method Stack

Classification should follow a deterministic precedence stack. Earlier methods override later methods.

1. Manual Arranger override
2. Exact ticker / issuer / instrument rule
3. Fund or index look-through rule
4. Manager / sleeve / mandate rule
5. Sector / industry / geography rule
6. LLM-assisted semantic classification
7. Review-required fallback

Policy:

- Hard curated rules override LLM suggestions.
- Manual overrides must include reviewer, timestamp, reason, and applicable lens version.
- Exact identifier rules should be preferred for public issuers, common indexes, and recurring fund instruments.
- Fund or index look-through rules should be used when holdings coverage is good enough to justify the bucket.
- Manager, sleeve, and mandate rules are useful for opaque or private holdings when position-level look-through is unavailable.
- Sector, industry, and geography rules are lower-confidence defaults and should be explicit about caveats.
- LLM assistance can propose a bucket, flags, confidence, and rationale, but it does not directly publish final product decisions.
- All assignments must validate against the lens's allowed bucket ids and flag ids.
- Uncertain assignments route to review instead of inventing a category.

## 7. LLM-Assisted Classification Policy

An LLM may be used internally to assist classification when deterministic rules do not resolve the position.

The LLM should receive:

- one thesis lens definition;
- approved bucket definitions;
- inclusion and exclusion rules;
- secondary flag definitions;
- one position evidence packet;
- a strict JSON output schema.

The LLM must:

- choose exactly one primary bucket from allowed bucket ids;
- optionally choose secondary flags from allowed flag ids;
- not invent categories, bucket ids, or flag ids;
- provide confidence;
- provide a short rationale;
- list missing evidence;
- mark `review_required` when uncertain.

The LLM must not:

- create new buckets;
- change lens definitions;
- create valuation outputs;
- create scenario impacts;
- make client-facing claims directly;
- bypass validation or human review.

Sample internal prompt structure:

```text
System:
You are an internal Arranger classification assistant. You classify one position under one approved thesis lens. You do not create valuation outputs, scenario impacts, investment recommendations, or client-facing copy.

Thesis lens:
{lens_id, lens_version, display_name, purpose}

Allowed primary buckets:
{bucket_id, display_name, definition, include_when, exclude_when}

Allowed secondary flags:
{flag_id, display_name, definition}

Assignment policy:
- Select exactly one primary_bucket_id.
- Select zero or more secondary_flag_ids from the allowed list.
- If evidence is insufficient, use the review bucket or set review_required true.
- Do not invent ids.
- Return only JSON that matches the schema.

Position evidence packet:
{position_evidence_packet_json}

Output schema:
{
  "primary_bucket_id": "string from allowed bucket ids",
  "secondary_flag_ids": ["strings from allowed flag ids"],
  "confidence": "high | medium | low | review_required",
  "rationale": "short internal rationale",
  "missing_evidence": ["field ids"],
  "review_required": true
}
```

Validation must reject LLM output if the primary bucket is missing, the bucket id is not allowed, flag ids are not allowed, confidence is invalid, required fields are missing, or the rationale makes unsupported client-facing claims.

## 8. Position-To-Thesis Assignment Algorithm

The assignment algorithm should produce one validated assignment per in-scope position per selected lens.

```python
def build_position_evidence_packet(position, available_sources):
    evidence = {
        "position_id": position.position_id,
        "instrument_id": position.instrument_id,
        "ticker": position.ticker,
        "issuer": position.issuer,
        "company_name": position.company_name,
        "security_type": position.security_type,
        "asset_class": position.asset_class,
        "sector": position.sector,
        "industry": position.industry,
        "geography": position.geography,
        "currency": position.currency,
        "manager": position.manager,
        "sleeve": position.sleeve,
        "mandate": position.mandate,
        "account": position.account,
        "holdings_lookthrough": available_sources.lookup_holdings(position),
        "business_description": available_sources.lookup_business_description(position),
        "revenue_segments": available_sources.lookup_revenue_segments(position),
        "supply_chain_geography": available_sources.lookup_supply_chain(position),
        "fund_manager_description": available_sources.lookup_manager_description(position),
        "valuation_coverage_status": position.valuation_coverage_status,
        "data_freshness": available_sources.data_freshness(position),
        "existing_tags": position.existing_tags,
        "human_notes": available_sources.human_notes(position),
        "source_metadata": available_sources.source_metadata(position),
    }
    evidence["missing_evidence_fields"] = find_missing_fields(evidence)
    return evidence
```

```python
def classify_position_under_lens(position_evidence, thesis_lens):
    assignment = apply_manual_override(position_evidence, thesis_lens)
    if assignment:
        return publish_position_thesis_assignment(assignment)

    assignment = apply_exact_identifier_rules(position_evidence, thesis_lens)
    if assignment:
        return publish_position_thesis_assignment(assignment)

    assignment = apply_fund_lookthrough_rules(position_evidence, thesis_lens)
    if assignment:
        return publish_position_thesis_assignment(assignment)

    assignment = apply_manager_mandate_rules(position_evidence, thesis_lens)
    if assignment:
        return publish_position_thesis_assignment(assignment)

    assignment = apply_sector_geography_rules(position_evidence, thesis_lens)
    if assignment:
        return publish_position_thesis_assignment(assignment)

    llm_suggestion = call_llm_classifier(position_evidence, thesis_lens)
    if llm_suggestion and validate_llm_assignment(llm_suggestion, thesis_lens):
        assignment = approve_llm_suggestion_after_policy_check(
            position_evidence=position_evidence,
            thesis_lens=thesis_lens,
            llm_suggestion=llm_suggestion,
        )
        if assignment:
            return publish_position_thesis_assignment(assignment)

    return route_to_review(position_evidence, thesis_lens, llm_suggestion)
```

```python
def apply_manual_override(position_evidence, thesis_lens):
    override = thesis_lens.manual_overrides.get(position_evidence["position_id"])
    if not override:
        return None
    return make_assignment(
        position_evidence=position_evidence,
        thesis_lens=thesis_lens,
        primary_bucket_id=override.primary_bucket_id,
        secondary_flag_ids=override.secondary_flag_ids,
        assignment_method="manual_override",
        confidence=override.confidence,
        rationale=override.rationale,
        review_status="approved",
        source_metadata=override.source_metadata,
    )
```

```python
def apply_exact_identifier_rules(position_evidence, thesis_lens):
    for key in ["instrument_id", "ticker", "issuer"]:
        identifier = position_evidence.get(key)
        if not identifier:
            continue
        rule = thesis_lens.identifier_rules.get((key, identifier))
        if rule:
            return make_rule_assignment(position_evidence, thesis_lens, rule, "identifier_rule")
    return None
```

```python
def apply_fund_lookthrough_rules(position_evidence, thesis_lens):
    lookthrough = position_evidence.get("holdings_lookthrough")
    if not lookthrough or not lookthrough.meets_quality_threshold:
        return None
    rule_result = evaluate_lookthrough_against_lens(lookthrough, thesis_lens)
    if rule_result.is_decisive:
        return make_rule_assignment(position_evidence, thesis_lens, rule_result, "fund_lookthrough_rule")
    return None
```

```python
def apply_manager_mandate_rules(position_evidence, thesis_lens):
    for field in ["manager", "sleeve", "mandate"]:
        value = position_evidence.get(field)
        rule = thesis_lens.manager_mandate_rules.get((field, value))
        if rule:
            return make_rule_assignment(position_evidence, thesis_lens, rule, "manager_mandate_rule")
    return None
```

```python
def apply_sector_geography_rules(position_evidence, thesis_lens):
    candidate = evaluate_sector_industry_geography(
        sector=position_evidence.get("sector"),
        industry=position_evidence.get("industry"),
        geography=position_evidence.get("geography"),
        thesis_lens=thesis_lens,
    )
    if candidate and candidate.confidence in {"high", "medium"}:
        return make_rule_assignment(position_evidence, thesis_lens, candidate, "sector_geography_rule")
    return None
```

```python
def call_llm_classifier(position_evidence, thesis_lens):
    prompt = build_strict_classification_prompt(position_evidence, thesis_lens)
    response = internal_llm_client.classify(prompt)
    return parse_json_response(response)
```

```python
def validate_llm_assignment(llm_suggestion, thesis_lens):
    if llm_suggestion["primary_bucket_id"] not in thesis_lens.allowed_bucket_ids:
        return False
    if any(flag_id not in thesis_lens.allowed_flag_ids for flag_id in llm_suggestion["secondary_flag_ids"]):
        return False
    if llm_suggestion["confidence"] not in {"high", "medium", "low", "review_required"}:
        return False
    if unsupported_claims_detected(llm_suggestion["rationale"]):
        return False
    return True
```

```python
def approve_llm_suggestion_after_policy_check(position_evidence, thesis_lens, llm_suggestion):
    if llm_suggestion["review_required"]:
        return None
    if llm_suggestion["confidence"] not in {"high", "medium"}:
        return None
    if requires_human_review(position_evidence, llm_suggestion, thesis_lens):
        return None

    return make_assignment(
        position_evidence=position_evidence,
        thesis_lens=thesis_lens,
        primary_bucket_id=llm_suggestion["primary_bucket_id"],
        secondary_flag_ids=llm_suggestion["secondary_flag_ids"],
        assignment_method="llm_assisted_after_validation",
        confidence=llm_suggestion["confidence"],
        rationale=llm_suggestion["rationale"],
        missing_evidence=llm_suggestion["missing_evidence"],
        review_status="approved_by_policy",
        source_metadata={"llm_assisted": True},
    )
```

```python
def route_to_review(position_evidence, thesis_lens, llm_suggestion=None):
    return make_assignment(
        position_evidence=position_evidence,
        thesis_lens=thesis_lens,
        primary_bucket_id=thesis_lens.review_required_bucket_id,
        secondary_flag_ids=[],
        assignment_method="review_required_fallback",
        confidence="review_required",
        rationale="Evidence was insufficient or ambiguous under the approved lens rules.",
        missing_evidence=position_evidence["missing_evidence_fields"],
        review_status="pending_review",
        source_metadata={"llm_suggestion": summarize_internal_suggestion(llm_suggestion)},
    )
```

```python
def publish_position_thesis_assignment(assignment):
    validate_assignment_against_lens(assignment)
    return {
        "lens_id": assignment.lens_id,
        "lens_version": assignment.lens_version,
        "position_id": assignment.position_id,
        "primary_bucket_id": assignment.primary_bucket_id,
        "secondary_flag_ids": assignment.secondary_flag_ids,
        "assignment_method": assignment.assignment_method,
        "confidence": assignment.confidence,
        "rationale": assignment.rationale,
        "missing_evidence": assignment.missing_evidence,
        "review_status": assignment.review_status,
        "reviewer_notes": assignment.reviewer_notes,
        "source_metadata": assignment.source_metadata,
    }
```

## 9. Confidence And Review Policy

Assignment confidence should use four levels:

- `high`
- `medium`
- `low`
- `review_required`

Suggested policy:

- High-confidence public issuer, ticker, or instrument rules may be auto-approved after validation.
- Medium-confidence assignments may be used in advisor review with concise caveat language.
- Low-confidence assignments should be treated directionally and should not support strong client-facing claims without review.
- Opaque private funds, manager-level holdings, or positions with weak look-through should route to review before strong client-facing claims.
- Large market-value positions with low confidence should be prioritized for review.
- Review queues should sort by exposure size, classification ambiguity, scenario impact relevance, and evidence quality.

Review sorting:

```python
def score_review_priority(position, assignment, revaluation_result=None):
    exposure_score = abs(position.market_value)
    ambiguity_score = confidence_to_ambiguity_score(assignment.confidence)
    data_quality_score = missing_evidence_score(assignment.missing_evidence)
    impact_score = abs(revaluation_result.impact) if revaluation_result else 0

    return weighted_sum(
        exposure_score=exposure_score,
        ambiguity_score=ambiguity_score,
        data_quality_score=data_quality_score,
        impact_score=impact_score,
    )
```

## 10. Published Mapping Artifacts

Arranger should publish versioned mapping artifacts that Arangur can consume without exposing internal evidence packets or raw LLM reasoning by default.

### `thesis_lens_catalog.json`

Purpose: lists approved thesis lenses available for advisor selection and report compatibility.

Required fields:

- `schema_version`
- `pack_id`
- `pack_version`
- `lenses`
- `approval_metadata`

Advisor-facing:

- lens display name;
- advisor-safe description;
- supported scopes;
- supported report elements;
- caveats.

Internal by default:

- rule internals;
- evidence packet requirements;
- LLM prompt templates;
- review queue details.

### `ai_adoption_lens_v1.json`

Purpose: defines the approved AI Adoption thesis lens.

Required fields:

- `schema_version`
- `lens_id`
- `lens_version`
- `display_name`
- `purpose`
- `primary_buckets`
- `secondary_flags`
- `neutral_bucket_id`
- `review_required_bucket_id`
- `assignment_policy`
- `validation_rules`
- `approval_metadata`

Advisor-facing:

- bucket labels;
- short advisor-safe bucket descriptions;
- lens caveats.

Internal by default:

- inclusion/exclusion rule detail;
- deterministic mapping rules;
- LLM prompt instructions;
- raw evidence requirements.

### `deglobalization_lens_v1.json`

Purpose: defines the approved Deglobalization / Isolationism lens with mutually exclusive primary buckets and optional secondary flags.

Required fields match the lens schema above.

### `geopolitical_bloc_lens_v1.json`

Purpose: defines the approved Cold War / Geopolitical Bloc lens with mutually exclusive primary buckets and optional secondary flags.

Required fields match the lens schema above.

### `position_thesis_assignments_ai_adoption_v1.json`

Purpose: publishes one primary bucket assignment per in-scope position under the AI Adoption lens.

Required fields:

- `schema_version`
- `lens_id`
- `lens_version`
- `portfolio_snapshot_id`
- `valuation_date`
- `assignment_scope`
- `review_required_bucket_id`
- `assignments`
- `coverage_summary`
- `review_summary`
- `source_metadata`

Each assignment should include:

- `position_id`
- `primary_bucket_id`
- `secondary_flag_ids`
- `assignment_method`
- `confidence`
- `rationale`
- `missing_evidence`
- `review_status`
- `reviewer_notes`
- `source_metadata`

Advisor-facing:

- approved bucket assignment;
- confidence or review caveat if needed;
- concise advisor-safe rationale only if deliberately exposed by a report element.

Internal by default:

- raw evidence packet;
- raw LLM response;
- reviewer work notes not approved for client use.

### `position_thesis_assignments_deglobalization_v1.json`

Purpose: publishes position assignments for the Deglobalization / Isolationism lens.

Required fields match the assignment artifact schema above.

### `position_thesis_assignment_manifest.json`

Purpose: binds lens schemas and position assignment files into one published mapping bundle.

Required fields:

- `schema_version`
- `pack_id`
- `pack_version`
- `portfolio_snapshot_id`
- `valuation_date`
- `lens_artifacts`
- `assignment_artifacts`
- `approval_metadata`
- `compatibility`

Relationship to generated reports:

- Arangur report elements consume approved mapping artifacts to aggregate base value, scenario value, and impact by thesis bucket.
- Generated reports should show advisor-safe bucket labels, totals, confidence summaries, caveats, and optionally concise rationale.
- Generated reports should not expose raw evidence packets, raw LLM reasoning, review work queues, or mapping-rule internals unless a future advisor-review report deliberately includes them.

## 11. Interaction With Full Revaluation

Thesis lens mapping starts after valuation has produced position-level values and impacts.

Position valuation coverage mapping happens before this step. It determines whether each position was valued directly, valued with substitute input, valued with approved policy, held at mark, routed to review, or not valued. Thesis buckets then aggregate those already-produced valuation results and preserve the coverage/confidence caveats.

Workflow:

1. Full valuation engine calculates base position values and base portfolio value.
2. Scenario market-state construction produces a complete scenario market state.
3. Full valuation engine calculates scenario position values and scenario portfolio value.
4. Revaluation bundle contains position-level base value, scenario value, impact, coverage, and confidence.
5. Selected thesis lens assigns each position to one primary bucket.
6. Report layer aggregates base value, scenario value, impact, and confidence by thesis bucket.
7. Advisor sees thesis-bucket attribution, not mapping machinery.

```python
def aggregate_revaluation_by_thesis_bucket(revaluation_results, position_thesis_assignments):
    bucket_rows = {}

    assignment_by_position = {
        row["position_id"]: row
        for row in position_thesis_assignments["assignments"]
    }

    for position_result in revaluation_results["position_results"]:
        assignment = assignment_by_position.get(position_result["position_id"])
        if assignment is None:
            bucket_id = position_thesis_assignments["review_required_bucket_id"]
            assignment_confidence = "review_required"
        else:
            bucket_id = assignment["primary_bucket_id"]
            assignment_confidence = assignment["confidence"]

        bucket = bucket_rows.setdefault(bucket_id, {
            "primary_bucket_id": bucket_id,
            "base_value": 0,
            "scenario_value": 0,
            "impact": 0,
            "position_count": 0,
            "confidence_mix": {},
            "coverage_mix": {},
            "top_positions": [],
        })

        bucket["base_value"] += position_result["base_value"]
        bucket["scenario_value"] += position_result["scenario_value"]
        bucket["impact"] += position_result["impact"]
        bucket["position_count"] += 1
        increment(bucket["confidence_mix"], assignment_confidence)
        increment(bucket["coverage_mix"], position_result["scenario_coverage_status"])
        maybe_add_top_position(bucket["top_positions"], position_result)

    return summarize_bucket_rows(bucket_rows)
```

Because v1 uses exactly one primary bucket per lens, total bucket base value, scenario value, and impact reconcile to the selected scope before any filtering or caveat display.

## 12. Advisor-Facing Consumption Rules

Advisor may:

- select an approved thesis lens;
- select a portfolio scope;
- select a compatible report element;
- view bucket-level base value, scenario value, impact, and confidence attribution;
- see concise confidence or review caveats;
- see advisor-safe bucket descriptions and approved scenario/lens language.

Advisor may not:

- create live thesis categories;
- edit mapping rules;
- see raw LLM classifications by default;
- see raw evidence packets by default;
- override thesis mapping in the main app unless a future internal/admin workflow explicitly supports it;
- use thesis buckets as valuation models;
- use thesis buckets as scenario construction controls.

## 13. Implementation Sequencing Recommendation

Recommended next tranches:

A. Add thesis lens contract fixtures.

B. Add a position evidence packet format.

C. Add a deterministic rule-based assignment skeleton.

D. Add an LLM-assisted classification design stub and offline prompt template, without live API calls.

E. Generate synthetic demo position-thesis assignments.

F. Map revaluation impacts by thesis bucket.

G. Then return to report views.

This sequencing keeps the architecture honest: lenses are approved classification artifacts, assignments are post-valuation mappings, and advisor reports consume approved outputs rather than creating classification systems live.

## 14. Open Questions For Frank

1. Which thesis lens should be product-grade first: AI Adoption, Deglobalization, Geopolitical Bloc, Energy Security, Credit Stress, or Private Liquidity?
2. Should v1 stay primary bucket only plus secondary flags, with no weighted splits?
3. Which evidence fields are essential for public companies?
4. Which evidence fields are essential for private funds, manager-level holdings, or opaque positions?
5. Should LLM-assisted classifications be auto-approved for high-confidence public tickers, or always sampled for review?
6. Should clients ever see rationale text, or only bucket labels and confidence/review caveats?
7. How should unresolved positions appear in client briefings versus advisor reviews?
8. Should large low-confidence positions block a thesis-bucket client report, or appear with explicit review-required caveats?
