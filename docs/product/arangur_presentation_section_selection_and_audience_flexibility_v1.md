# Arangur Presentation Section Selection and Audience Flexibility v1

Status: implemented local product contract
Date: 2026-07-16
Product: Arangur

## Decision

The advisor controls which populated, presentable Briefing Sections appear in Preview and Presentation. Intended audience supplies defaults, wording, suggested depth, sequence, and labels; it does not prohibit an advisor from selecting an otherwise presentable section.

The shared rule is:

> Reviewed + at least one selected populated presentable Briefing Section + no true presentation-blocking condition = Preview eligible.

Ready to Present requires Reviewed and Preview eligibility plus an explicit advisor action. Presentation eligibility requires Ready to Present and the same Preview eligibility. Status alone cannot create eligibility.

## Four section states

### Included by default

The section is populated, presentable, and recommended for the intended audience. The advisor may keep, remove, or reorder it.

### Excluded by default

The section is populated and presentable but is not initially recommended for the intended audience. Advisor-review and advisor-only classifications normally produce this state for a client audience. The advisor may explicitly include, remove, or reorder the section.

### Unavailable

The section has no real rendered content. It cannot be selected or presented. Prepare for Presentation shows the title and a concise availability reason; Arangur does not fabricate output.

### Protected internal material

The item is not an ordinary presentable Briefing Section. One shared classifier recognizes `developer_qa`, `raw_metadata`, `diagnostic_payload`, `candidate_proxy_approval`, `internal_control`, `unapproved_method`, and `unapproved_mapping`. `unavailable_output` is classified separately as unavailable.

Advisor-oriented is not synonymous with protected. `advisor_review`, `advisor_only`, detailed advisor attribution, and manager-oversight content remain selectable when they contain real output and do not carry a protected classification.

## Audience defaults

- Client: populated `client_facing` sections are selected by default. Other populated presentable sections remain available.
- Manager discussion: populated `manager_discussion`, `manager_review`, current manager-oriented `advisor_review`, and client-facing sections are recommended. Other populated presentable sections remain available.
- Advisor/internal: populated advisor-review, advisor-only, and manager-review sections may be selected by default. Advisor/internal origin never prohibits presentation.
- External Manager Story Translation: Manager Story Summary and Governance/Caveat Note are the safe defaults. Implied Lenses and Key-Price Scenario Set remain protected until their mapping or method is approved. Candidate Benchmark/Proxy Map is protected and requires approval. Gated report output remains unavailable.

## Selection lifecycle

After Advisor Review is complete, **Prepare for Presentation** opens the focused selection screen. It shows the Dated Briefing title, intended audience, counts, recommended state, purpose, original audience recommendation, selected order, unavailable sections, and protected-item summaries.

The advisor may include, exclude, move, select recommended defaults, select all presentable sections, or reset to the recommended selection. **Save Presentation Selection** persists the exact selected IDs and order on the same Dated Briefing and returns to Advisor Review. A changed selection resets active presentation progress to the first selected section without changing the immutable populated content.

## Preview and Presentation

Preview renders the exact saved selection in the exact saved order. It does not reapply the original audience recommendation as a second filter. Unselected, unavailable, protected, and Developer / QA material stays out.

Presentation consumes the same helper and sequence as Preview. It preserves Previous/Next, section index, Explain/Verify, exit context, and Resume progress. It cannot introduce an excluded section or remove a selected section because of its original audience recommendation.

## Dated Briefing record

The compatible browser-local record now normalizes and stores:

- `presentation_section_ids`;
- `presentation_section_order`;
- `presentation_selection_updated_at`;
- `presentation_selection_source` (`recommended_defaults`, `advisor_customized`, or `legacy_migration`);
- `intended_audience`;
- `presentation_status`;
- derived `preview_eligible`;
- `presentation_progress`, plus compatible historical timestamps and position.

Internal IDs are not shown in ordinary advisor UI.

## Legacy migration

Existing Dated Briefings are retained. Where safe, earlier client/audience populated sections or an explicit saved presentation sequence become the migrated selection. Advisor-only populated sections remain in the inventory and can be selected later. If no safe earlier sequence exists, audience recommendations initialize a revisable selection, but uncertain legacy readiness is not promoted. Explicit contradictory readiness is normalized to Reviewed, with migration notes in Developer / QA.

## External-story restrictions

The presentation selector preserves these caveats: Translated external viewpoint; Not verified; Not endorsed; Not a recommendation; Candidate proxies require approval. Candidate proxy approval data, raw implied mapping details, unapproved scenario/lens construction, Developer / QA material, and internal-control artifacts cannot be selected.

## Developer / QA boundary

Developer / QA shows intended audience; populated, presentable, protected, and unavailable counts; recommended and saved selections; selection source/time; Preview, Ready, Presentation, and Resume decisions; storage version; and migration notes. Raw IDs and normalization detail remain subordinate to ordinary advisor work.

## Explicit deferral

This tranche does not redesign populated Briefing Section visuals, import Design Lab HTML, add analytics, add reports, change calculations, add dependencies, change deployment, or implement production persistence. The next tranche remains **Arangur Dated Briefing Reader and Design-Lab Visual Integration v1**.
