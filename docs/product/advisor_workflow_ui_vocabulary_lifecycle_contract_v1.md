# Advisor Workflow UI Vocabulary and Lifecycle Contract v1

Status: approved by Frank and locally implemented for the synthetic demo, 2026-07-15

Canonical product name: **Arangur**. Existing filenames, directories, commits, and historical artifacts containing `ARRANGER` are not renamed.

## Vocabulary contract

| Concept | Internal canonical term | Advisor-facing term | Client-facing term | Legacy/avoid term in ordinary UI | Rationale/status |
| --- | --- | --- | --- | --- | --- |
| Ordered catalog definition for an audience/use case | `workflow` | **Briefing type** for built-ins | Not shown | Workflow ID, pipeline, run type | Preserve the repo contract without making system structure the product. Recommended; Frank approval required. |
| Reusable editable definition | `briefing_template` / current workflow payload | **Briefing template** | Not shown | Workflow template, saved workflow, report set | Distinguishes reusable intent from a dated output. Recommended; Frank approval required. |
| Dated generated output | `generated_report_artifact` | **Briefing** | **Briefing** | Generated report, run, artifact | A briefing is fixed to generated/data dates and can be read or presented. Recommended; Frank approval required. |
| Ordered content inside a template | `client_briefing_set` / `advisor_review_set` | **Sections** or **briefing sections** | Section titles only | Briefing set, report set | Avoid a third saved product object. Accepted recommendation. |
| Reusable report capability | `report_family` / `report_element` / `report_view` | **Section type** only in template editing | Plain-English section title | Report element, view ID, renderer | Keep taxonomy internal; expose the question answered. Accepted recommendation. |
| Internal approval surface | `advisor_review` | **Advisor Review** | Not shown | Admin preview | Makes review/approval distinct from rehearsal. Accepted concept; defaults need Frank review. |
| Exact rehearsal of client content | `client_preview` | **Client Preview** | Not shown as a mode label | Client mode, render preview | Must reproduce exactly what the client would see. Recommended. |
| Audience-facing delivery | `presentation` | **Present** / **Presentation** | No mode label beyond progress | Slideshow engine, presenter object | Hides authoring, generation, export, and administration. Accepted. |
| Claim-bound support | `evidence` | **Explain** then **Verify** | Explain / Evidence when requested | Analysis library, source browser | Preserves the Understand → Explain → Verify → return path. Accepted. |
| Missing prerequisite | `gated` or `deferred` | **Not ready** with a reason | Hidden unless material to an approved client statement | Failed, coming soon, unavailable report | Calmly states the missing prerequisite and never invents output. Accepted. |
| Analytical/control-only content | `diagnostic` | **Advisor diagnostic** when explicitly opened | Hidden | Client report | Avoids confusing calculation/control material with a client answer. Accepted. |
| Basis/coverage prerequisite | `setup_readiness` | **Preparation note** or **Needs review** | Hidden unless material caveat | Readiness report | A readiness artifact may support the advisor but cannot replace the client answer. Accepted. |
| Internal reconciliation-only content | `internal_control` | **Reconciliation** in Developer / QA or protected advisor depth | Hidden | Client evidence | Keeps layer handoffs and technical tie-outs out of the ordinary conversation. Accepted. |

## Banned or avoided ordinary-UI language

The advisor/client path must not expose prompt, model, agent, workflow ID, run ID, job status, pipeline, schema, JSON, API, cache, database ID, artifact path, filename, source ID, retrieval configuration, token, component, renderer, or internal status code. These may appear only in Developer / QA or governed technical evidence. Sources: design-lab instructions and `docs/contracts/report_element_information_budget_v1.md`.

`Workflow` may appear in Developer / QA and code/contracts. It is not the recommended heading for the first screen. `Generated Report` remains a current-app/contract alias until implementation migration, but new user-facing prose should use `Briefing`.

## Object model

The recommended v1 user-facing model contains two saved objects:

1. **Briefing template** — reusable definition of audience, purpose, ordered sections, visibility, optionality, and fixed caveats.
2. **Briefing** — immutable dated output created from one template and one data snapshot.

Portfolio is existing business context, not created by this flow. Advisor Review, Client Preview, Presentation, and Evidence are states/views, not additional saved objects. `Report set`, `briefing set`, `generated report`, and `alignment review` do not become new general-purpose saved objects in v1.

## Lifecycle diagram

```text
Built-in briefing type
  -> open approved briefing template
  -> duplicate/edit bounded fields (optional)
  -> save custom briefing template (optional)
  -> confirm portfolio, audience, data date, readiness
  -> create briefing with current data
  -> Advisor Review
  -> Client Preview (when client-facing)
  -> Presentation
  -> immutable Historical Reading

Any conclusion
  -> Explain
  -> Verify / exact evidence
  -> return to the same conclusion and position

Historical briefing
  -> Create briefing with current data
  -> new briefing object; historical briefing remains unchanged
```

## Lifecycle rules

1. **Current data always creates a new briefing.** It never mutates an existing dated briefing.
2. **Generated briefings are immutable.** Corrections or refreshed data create a new briefing with lineage to the source template and, when applicable, the prior briefing.
3. **Templates are reusable and editable.** Built-ins remain read-only; editing a built-in creates an unsaved working copy that must be saved as a custom template.
4. **Client Preview is not persistence.** It is the exact client-visible rendering of the reviewed briefing.
5. **Presentation does not alter content.** It changes controls and focus only.
6. **Evidence is date-bound.** Evidence opened from a briefing uses the briefing's data snapshot and returns to the exact originating claim.
7. **Historical reading is fixed.** The generated date and data-as-of date remain visible; a current-data action is explicitly generative.
8. **Durable backend history is later work.** The UI wiring tranche may preserve browser-local demo behavior while honoring immutable semantics. Production persistence, retention, versioning, tenancy, and audit require a separate approved tranche.

## State transitions

| From | Action | To | Rule |
| --- | --- | --- | --- |
| Home | Choose briefing type + Continue | Template Selection / Configure | One choice; internal workflow ID remains hidden. |
| Home | Open a prior briefing | Historical Items | Secondary path. |
| Template Selection | Use template | Configure / Confirmation | Only consequential fields. |
| Template Selection | Duplicate | Builder | Built-in is not changed. |
| Builder | Save template | Template Selection / saved state | Does not generate a briefing. |
| Configure | Create briefing with current data | Advisor Review | Creates new dated object. |
| Advisor Review | Preview for client | Client Preview | Only approved client-visible sections. |
| Advisor Review | Present | Presentation | Allowed for advisor-only workflow without Client Preview only when there is no client audience. |
| Client Preview | Present | Presentation | Content identical; chrome reduced. |
| Presentation | Exit | Prior Preview/Reader position | Exact position preserved. |
| Claim | Explain | Explanation | One layer of comparison/composition/causality. |
| Explanation | Verify | Evidence | Exact values, sources, assumptions, tables. |
| Evidence | Back | Originating claim | Exact state/scroll/step restored. |
| Historical briefing | Create with current data | Configure / Advisor Review | New briefing; original remains immutable. |

## Legacy/current-app mapping

| Current app/code term | Contract mapping | Migration implication for later wiring |
| --- | --- | --- |
| Briefing Templates | Briefing templates | Keep. |
| Built-in workflow payload | Built-in briefing type backed by a briefing template | Hide workflow ID; keep deterministic mapping. |
| Saved workflow | Custom briefing template | Rename in visible prose; storage schema may remain. |
| Generate with current data | Create briefing with current data | Recommended label; always creates a new dated object. |
| Generated Reports | Briefings / Prior briefings | Rename visible collection after Frank approval. |
| Client Briefing Workflow | Client briefing sections | Avoid exposing workflow as the editable set name. |
| Advisor Review Workflow | Advisor Review sections | Keep Advisor Review; avoid workflow suffix. |
| Populate workflow | Create briefing | Remove operational wording from ordinary UI. |
| Preview Client Briefing | Client Preview | Keep concept; ensure exact client visibility. |
| Preview Advisor Review | Advisor Review | Review is not a client preview. |
| Current Draft Workflow | Draft briefing template | Rename visible heading. |
| Copy Workflow / Save As New | Duplicate template / Save as new template | Preserve behavior with clearer object identity. |
| Browser-local generated report shelf | Browser-local briefing history | Treat as demo-only approximation of future durable history. |

## Approval gate

Frank must approve the two-object model, `Briefing type` label, `Briefing` for generated output, immutable/current-data semantics, and the deferral of durable production history before UI wiring.
