# Local Briefing Spec Set Contract v1

Status: implemented browser-local baseline.

## Purpose

The local briefing spec set is the browser-only export shape for the current
Report Element Finder / Composer state. It proves that the composer can produce
a clean, portable ordered-set artifact before backend persistence or report
generation exists.

This contract covers the frontend export/import shape only. It does not create
database records, report packages, generated reports, analytics outputs,
workflow runs, or production client-ready briefings.

## Schema

The browser emits:

- `schema_version`: `arangur.local_briefing_spec_set.v1`
- `exported_at`: browser timestamp for the local export action
- `synthetic_data`: `true`
- `client_context`: compact demo context
- `client_briefing_set`: ordered list of Client Briefing Set specs
- `advisor_review_set`: ordered list of Advisor Review Set specs

The current client context includes:

- `client_family`
- `portfolio_context`
- `data_status`
- `valuation_confidence`
- `review_item_count`

## Ordered Set Shape

`client_briefing_set` and `advisor_review_set` are arrays. Array order is the
set order. Each item also includes an explicit one-based `order` field for
readability and future compatibility.

Client and advisor sets use the same item envelope so analytic and narrative
elements can be interleaved in a single ordered sequence.

## Spec Fields

Each serialized spec includes:

- `order`
- `local_spec_id`
- `element_kind`: `analytic` or `narrative`
- `element_id` for analytic specs, otherwise `null`
- `element_title`
- `target_set`
- `target_branch`
- `placement`
- `advisor_internal_purpose` when applicable
- `configured_parameters`
- `preview_available`
- `matched_rendered_view`
- `confidence_badge`
- `caveat`

Narrative specs also include:

- `narrative_type`
- `narrative_fields`

## Matched Preview Metadata

When an analytic spec matches one of the committed rendered demo views, the
serialized `matched_rendered_view` object includes:

- `view_id`
- `element_title`
- `html_fragment_url`
- `markdown_fragment_url`

If no existing rendered view matches the configured spec, `preview_available`
is `false` and `matched_rendered_view` is `null`. The browser preview then
shows a placeholder instead of inventing content.

## Local-Only Limitations

The local spec set is not persisted by the backend and is not a durable system
of record. Copy, download, and restore actions happen in the browser. Restoring
an exported spec set repopulates only the current browser composer state.

The current local preview assembles existing rendered element fragments and
narrative text. It does not generate new analytics, call `/api/runs`, write
files, create reports, or use live data.

## Future Backend Path

A later persistence batch can adapt this envelope into a backend briefing-set
metadata model once product and data-model decisions are stable. That future
model should preserve:

- ordered Client Briefing Set and Advisor Review Set contents;
- template ids and configured parameters for analytic specs;
- narrative element type and fields;
- matched rendered-view metadata where relevant;
- synthetic-data and source-version metadata;
- clear separation between saved specs and generated report artifacts.

Backend persistence should not treat this browser-local timestamp or local spec
id as production-grade audit metadata without an explicit migration design.
