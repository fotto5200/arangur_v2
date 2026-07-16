# Arangur UI User Jobs v1

Status: Proposed for review
Scope: Interaction architecture only; no visual direction or implementation contract

## Working vocabulary

- **Briefing**: a dated, generated document whose claims and data are fixed to a stated as-of time. A briefing can be read, presented, shared, and reopened.
- **Briefing template**: a reusable definition of audience, objective, content emphasis, and recurring sections. It is not a generated document.
- **Alignment review**: a current assessment of whether managers and the overall portfolio remain consistent with mandates, investment themes, scenarios, and client objectives.
- **Evidence**: analysis, source material, calculations, and history supporting a visible conclusion. It appears only when requested.

These are the only interaction-level concepts needed for the jobs below. “Report” is treated as a plain-language synonym for a generated briefing, not as a second product object.

## Architectural failure patterns to avoid

The initial artifact was created before current-screen evidence was supplied. Eight subsequent screenshots show a template/report list with many peer actions, a control-heavy generated-report reader, repeated explanatory labels, and analytical reports dominated by headings, bullets, and wide numeric tables. The redesign treats those screens as capability evidence rather than a layout baseline and explicitly avoids these recurring failure patterns:

- exposing setup before useful output;
- making users choose among several equally prominent actions;
- mixing presentation, authoring, analysis, and administration in one state;
- presenting system structure as navigation;
- showing technical controls because the platform supports them;
- using explanatory labels to compensate for an unclear workflow;
- requiring users to reconstruct the relationship between a template, a current run, and a past generated briefing.

## Job 1 — Open and present an already-generated briefing

### User and immediate objective

An advisor, relationship manager, CIO, or investment lead needs to open a specific completed briefing and present it confidently to a client, committee, or internal audience.

### Minimum successful outcome

The correct briefing opens at its beginning, clearly identifies its audience and data date, is easy to advance, and does not expose editing, generation, or administrative controls during presentation.

### Shortest understandable interaction path

Open the briefing from a recent item, search result, or direct link → confirm title, audience, and as-of date → choose **Present** → advance through the briefing → exit back to the same reading position.

### Must be visible

- briefing title and intended audience;
- as-of date and, if material, a concise freshness warning;
- current section and clear next/previous movement;
- the briefing content itself, including conclusions, implications, and disclosed caveats;
- a single **Present** action before presentation;
- discreet access to evidence when the presenter asks for it;
- an obvious way to exit presentation.

### Hidden unless requested

- template definition and generation settings;
- alternative layouts or section configuration;
- editing and regeneration controls;
- the full source inventory;
- portfolio diagnostics not cited by this briefing;
- sharing permissions and administrative metadata;
- authoring history.

### Technical concepts that should not appear in the ordinary experience

Prompt, model, agent, workflow, run ID, job status, pipeline, context window, token count, retrieval, chunk, embedding, vector store, tool call, schema, JSON, API, cache, database identifier, or internal component name.

## Job 2 — Find a saved briefing template and generate a report with current data

### User and immediate objective

An advisor, investment professional, or client-service team member needs to reuse an approved briefing template for a known client or meeting using current portfolio and market data.

### Minimum successful outcome

The user selects the intended template, confirms the audience/portfolio and effective date, generates one briefing, and lands directly in the readable result with any freshness or coverage caveat disclosed.

### Shortest understandable interaction path

Find template by name, audience, or recent use → preview what it produces → choose **Use template** → confirm portfolio/audience and current-data date in one focused state → choose **Generate briefing** → read the completed briefing.

### Must be visible

- template name, purpose, owner/approval status when relevant, and last use;
- a concise preview of expected sections and audience;
- the selected portfolio or client;
- the proposed as-of date and whether required data is ready;
- any material missing-data warning before generation;
- one generation action;
- progress expressed in user terms only if generation is not immediate;
- the readable result and its as-of date.

### Hidden unless requested

- prompt text and system instructions;
- source selection and retrieval rules;
- section-by-section generation parameters;
- model choice and generation diagnostics;
- data connector configuration;
- template version history;
- advanced overrides;
- raw execution log.

### Technical concepts that should not appear in the ordinary experience

Execution graph, orchestration, agent, model selector, temperature, seed, token budget, inference, prompt variables, retrieval configuration, source IDs, connector IDs, queue, worker, run ID, payload, or serialization format.

## Job 3 — Create or modify a reusable briefing template

### User and immediate objective

An investment content owner, research lead, or authorized advisor needs to define or revise a repeatable briefing for a stable meeting type or audience.

### Minimum successful outcome

The user creates or updates a template with a clear purpose, audience, recurring content, and emphasis; previews it with representative current data; and saves a reusable version without publishing an accidental live briefing.

### Shortest understandable interaction path

Open templates → choose an existing template or **New template** → define audience and purpose → select and order a small set of meaningful briefing sections → state emphasis and guardrails in plain language → preview with a representative portfolio → save.

### Must be visible

- template name, audience, and purpose;
- a short set of user-meaningful sections such as Executive view, Portfolio changes, Manager developments, Scenario implications, and Recommended discussion;
- section order and whether a section is required or conditional;
- plain-language emphasis and exclusions;
- representative preview content clearly marked as a preview;
- who can use the template, if access is material;
- a single **Save template** action;
- unsaved-change status.

### Hidden unless requested

- underlying prompt construction;
- field mappings and data bindings;
- formatting primitives;
- internal section IDs;
- data-query syntax;
- generation model configuration;
- detailed permission administration;
- version comparison and rollback;
- diagnostics.

### Technical concepts that should not appear in the ordinary experience

Prompt engineering, variables, placeholders, conditional expressions, schema, component tree, renderer, data binding, API field, query language, model parameters, agent instructions, tool permissions, or template serialization.

## Job 4 — Review portfolio and manager alignment

### User and immediate objective

A CIO, portfolio strategist, investment committee member, or senior advisor needs to determine whether each manager and the aggregate portfolio still align with mandates, investment themes, scenario expectations, and the client’s objectives—and identify what requires attention now.

### Minimum successful outcome

The user sees a current portfolio-level conclusion, the few material exceptions, why each exception matters, and the next review or decision required. They can move from portfolio conclusion to manager-level evidence without scanning every manager.

### Shortest understandable interaction path

Open the portfolio’s alignment review → read the overall conclusion and material changes → choose the highest-priority exception → inspect its mandate/theme/scenario/client-objective reasoning → mark for discussion or return to the portfolio view.

### Must be visible

- portfolio/client identity and as-of date;
- an overall conclusion expressed in plain language;
- what changed since the prior review;
- only material exceptions or emerging watch items, ordered by consequence;
- for each exception: affected manager or portfolio exposure, dimension of misalignment, significance, and recommended next step;
- clear distinction between confirmed issue, watch item, and insufficient evidence;
- a path to the supporting evidence;
- a single dominant action: examine the next material exception.

### Hidden unless requested

- fully aligned managers;
- every mandate criterion and theme mapping;
- scenario model mechanics;
- raw holdings, factor decompositions, and time series;
- low-materiality observations;
- scoring formulas and thresholds;
- data-quality diagnostics;
- administrative ownership and taxonomy management.

### Technical concepts that should not appear in the ordinary experience

Rule engine, classifier, confidence threshold, feature, factor pipeline, ontology, taxonomy ID, graph edge, mapping table, vector similarity, alert rule, batch calculation, data lineage ID, or internal score normalization.

## Job 5 — Inspect deeper analytical evidence

### User and immediate objective

An investment professional, skeptical committee member, or presenter responding to a question needs to verify a specific visible claim without losing the surrounding briefing or alignment-review context.

### Minimum successful outcome

The user sees the reasoning, relevant measures, time period, source, and caveats for one claim, can move one level deeper if necessary, and can return exactly where they were.

### Shortest understandable interaction path

Select **View evidence** beside a claim → review the concise evidence summary → optionally open a cited analysis or source → return to the same claim and reading position.

### Must be visible

- the claim being supported;
- a concise explanation of how the evidence supports or qualifies it;
- relevant values, comparisons, and time period;
- data as-of date;
- named sources in user-recognizable terms;
- assumptions, caveats, and contradictory evidence;
- clear return to context;
- one dominant next action, usually **Open analysis** or **Back to briefing**.

### Hidden unless requested

- unrelated analyses and sources;
- raw records and full data tables;
- calculation details beyond the level needed to assess the claim;
- source-ingestion status;
- provenance infrastructure;
- model reasoning traces;
- debugging information.

### Technical concepts that should not appear in the ordinary experience

Chain of thought, retrieval result, chunk, embedding, similarity score, tool output, hidden reasoning, source object ID, database table, query plan, notebook cell, pipeline stage, or machine confidence presented as certainty.

## Job 6 — Find and reopen a prior generated briefing

### User and immediate objective

An advisor, investment professional, compliance reviewer, or client-service team member needs to locate a briefing generated in the past and reopen the exact dated version.

### Minimum successful outcome

The user finds the intended briefing by recognizable business attributes, can distinguish it from similar versions, and opens the immutable historical document without silently refreshing its data.

### Shortest understandable interaction path

Search or filter prior briefings by client, meeting, date, or template → identify the correct result from title, audience, generated date, and data date → open it at the beginning or resume the prior reading position.

### Must be visible

- search using business language;
- briefing title, client/audience, generated date, and data as-of date;
- template name when it helps distinguish similar briefings;
- author or presenter when relevant;
- a clear historical indicator;
- one dominant **Open briefing** action;
- a warning before any action that would create a new current-data version.

### Hidden unless requested

- execution history;
- duplicate run details;
- file paths and storage locations;
- internal status codes;
- generation diagnostics;
- technical version identifiers;
- archival and retention administration;
- bulk operations.

### Technical concepts that should not appear in the ordinary experience

Artifact ID, run ID, blob, object store, snapshot hash, cache key, database record, job status, environment, branch, build, or raw timestamp format.

## Cross-job interaction contract

- Generated briefings are immutable historical documents. “Use current data” creates a new briefing; it never rewrites an old one.
- A template and a generated briefing are visibly distinct and never share an edit state.
- Every briefing and alignment conclusion carries an understandable as-of date.
- Evidence opens in context and returns the user to the exact claim or exception.
- Presentation hides construction, editing, and administration.
- Ordinary users encounter business concepts, not the platform’s implementation model.
- Advanced, administrative, and technical controls live in separately entered surfaces and never appear merely because they are available.
