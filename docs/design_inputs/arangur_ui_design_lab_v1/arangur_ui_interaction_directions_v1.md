# Arangur UI Interaction Directions v1

Status: Three independent directions for review; none selected
Depends on: `arangur_ui_user_jobs_v1.md`
Scope: Interaction architecture only; no visual styling, mockups, implementation, or hybrid recommendation

## Shared boundaries

All three directions use the same product truths so that the comparison is about interaction architecture rather than vocabulary.

- A **briefing** is a dated, immutable generated document.
- A **briefing template** is a reusable setup, not a document.
- An **alignment review** assesses the current portfolio and its managers against mandates, themes, scenarios, and client objectives.
- **Evidence** is opened from a specific conclusion and returns to that conclusion.
- Generating with current data always creates a new briefing.
- Presentation never exposes authoring, generation, or administration.
- Internal concepts such as prompts, models, agents, workflows, runs, pipelines, schemas, source IDs, and retrieval configuration are absent from ordinary workflows.

The directions must be evaluated separately. Controls, navigation, or behaviors from one direction should not be added to another before a direction is selected.

---

# Direction 1 — The Briefing Desk

## Architectural premise

The generated document is the center of gravity. Arangur behaves like a calm briefing reader with creation, history, alignment, and evidence entered from the document context. Users begin with useful output, not a dashboard or a conversation.

## Entry point

Open the most recently used or directly linked briefing in reading mode. If there is no recent briefing, open a restrained “Briefing desk” containing only recent briefings and one dominant **Open briefing** action.

The persistent escape hatch is a compact destination switcher: Briefings, Alignment, Templates. It is navigational, never a multi-panel dashboard.

## Exact interaction paths for the primary jobs

### 1. Open and present an already-generated briefing

Briefing desk or direct link → **Open briefing** → briefing reader, beginning at the executive view → verify audience and as-of date → **Present** → presentation state → **Next** through sections → **Exit presentation** → same place in reader.

No generation or edit control is visible in the presentation state.

### 2. Find a saved template and generate with current data

Destination switcher → Templates → template finder → search by meeting, client type, or template name → **Open template** → template preview → **Use template** → single confirmation state showing portfolio/audience, current-data date, and any missing coverage → **Generate briefing** → preparation state → **Open briefing** → generated briefing reader.

The template’s construction details remain closed. The confirmation state asks only decisions that can materially change the result.

### 3. Create or modify a reusable template

Destination switcher → Templates → template finder → **New template** or open an existing template → definition state: purpose, audience, and meaningful sections → **Preview** → representative document preview → **Save template** → template preview with saved confirmation.

For an existing template: open template → **Edit template** → modify purpose, section order, emphasis, or exclusions → **Preview changes** → document preview with a concise “what changed” note → **Save template**.

There is no prompt editor, field mapper, or simultaneous generated-document editor.

### 4. Review manager and portfolio alignment

Destination switcher → Alignment → current portfolio conclusion → **Inspect priority exception** → exception page showing affected manager/exposure and the relevant mandate, theme, scenario, or client-objective conflict → **Review recommendation** → decision-oriented conclusion → **Back to portfolio** or move to the next exception.

Fully aligned managers stay collapsed behind **Show all managers**. The primary path follows exceptions, not the roster.

### 5. Inspect deeper analytical evidence

From a visible claim in a briefing or alignment exception → **View evidence** → contextual evidence sheet/page containing the claim, supporting measures, time period, sources, and caveats → **Open analysis** only if more depth is needed → detailed analysis → **Back to claim** → exact originating position.

The first evidence layer explains; the second exposes analytical depth. Raw source records are a separate, explicitly requested level.

### 6. Find and reopen a prior generated briefing

Destination switcher → Briefings → briefing finder → enter client, meeting, date, presenter, or template → results ordered by likely relevance → select result → **Open briefing** → immutable historical briefing reader with generated date and data as-of date visible.

If the user wants current data: reader’s secondary “Create current briefing” action → confirmation → a new briefing. The historical document is never overwritten.

## State contract

| Focused state | Dominant action | Above the fold | Hidden unless requested |
|---|---|---|---|
| Empty/recent briefing desk | **Open briefing** | Recent briefing titles, audience/client, generated date, data date; search entry | Templates, portfolio diagnostics, administration, bulk actions |
| Briefing finder/results | **Open briefing** | Search, business filters, best-matching results with audience and dates | Run metadata, technical versions, archives, generation diagnostics |
| Briefing reader | **Present** | Title, audience, as-of date, executive conclusion, current section | Template setup, generation controls, complete source list, editing, administration |
| Presentation | **Next** | Current section/content, discreet progress, exit | Navigation chrome, authoring, sharing setup, template, history, system state |
| Template finder | **Open template** | Search, recent/approved templates, purpose, audience, last used | Prompt/configuration, version graph, permissions administration |
| Template reuse preview | **Use template** | Purpose, audience, expected document sections, representative output excerpt | Edit controls, prompt, source bindings, model controls, internal fields |
| Template maintenance preview | **Edit template** | Purpose, audience, expected document sections, representative output excerpt | Generation action, prompt, source bindings, model controls, internal fields |
| Template definition/edit | **Preview** | Name, purpose, audience, ordered meaningful sections, emphasis/exclusions | Generation internals, field mappings, advanced access administration |
| Template document preview | **Save template** | Representative first page/section, changed elements, preview-data label | Technical diff, renderer controls, internal IDs |
| Generation confirmation | **Generate briefing** | Portfolio/audience, effective date, data-readiness summary, material caveat | Section micro-settings, sources configuration, model/run controls |
| Briefing preparation | **Open briefing** when ready | Plain-language status, selected portfolio/template, safe exit | Queues, workers, logs, percent theater, internal errors |
| Alignment summary | **Inspect priority exception** | Overall conclusion, what changed, top material exception, as-of date | Aligned-manager roster, scoring mechanics, raw analytics |
| Alignment exception | **Review recommendation** | Affected manager/exposure, misalignment dimension, consequence, concise reasoning | Other exceptions, full mandate mapping, scenario mechanics |
| Recommendation | **Back to portfolio** | Recommended discussion/decision, urgency, owner if known | Workflow automation, task administration, unrelated analyses |
| Evidence summary | **Back to claim** | Original claim, concise evidence, key values, period, sources, caveats; secondary access to full analysis | Raw records, unrelated sources, calculation internals |
| Detailed analysis | **Back to claim** | Selected analysis, assumptions, comparisons, source date | Debugging, ingestion state, query/pipeline details |

Entry intent creates a distinct focused state. Template reuse preview and template maintenance preview may share content, but they do not share an equal-weight action bar.

## What remains globally hidden

- system architecture and generation machinery;
- account, data-source, taxonomy, and permissions administration;
- bulk operations;
- low-materiality observations;
- complete data lineage;
- template internals while reading a briefing;
- historical briefings while presenting the current one.

## Strengths

- Best fit for opening, reading, and presenting finished work.
- Makes useful output the default and keeps the interface calm.
- Gives briefings a stable, trustworthy identity as dated documents.
- Evidence can remain anchored to a precise claim.
- Presentation is easy to understand because the reading object and presenting object are the same.
- Supports familiar document behaviors without exposing how the document was generated.

## Likely failure modes

- Portfolio alignment may feel secondary or buried because it is not inherently a document.
- Users who arrive without knowing which briefing they need may find a reader-oriented entry point too narrow.
- Template creation can be awkward if the document preview overemphasizes layout instead of content intent.
- A document can become a dumping ground for every analysis, defeating progressive disclosure.
- The destination switcher could quietly grow into conventional application navigation and dilute the document-first premise.
- Frequent switching between portfolios may require more navigation than in an object-centered architecture.

---

# Direction 2 — The Arangur Guide

## Architectural premise

The user states an objective in business language and Arangur guides the shortest path, asking only for missing consequential information. The conversation is the control surface; completed briefings, alignment conclusions, and evidence appear as focused outputs inside or beside the exchange. The assistant does not narrate system activity or expose its reasoning machinery.

## Entry point

A single guide state opens with the current user/portfolio context and the prompt: “What do you need to prepare or review?” Beneath it are a few concrete, personalized starting requests such as “Present the latest Investment Committee briefing,” “Prepare the quarterly client review,” and “Check portfolio alignment.” They are examples of jobs, not feature categories.

## Exact interaction paths for the primary jobs

### 1. Open and present an already-generated briefing

Guide → user asks “Open the May 12 Horizon Family briefing” or chooses a recent suggestion → if one exact match exists, briefing summary appears immediately → **Present briefing** → presentation state → **Next** → **Exit presentation** → returns to the briefing summary and conversation.

If multiple briefings plausibly match, the guide shows at most the few distinguishing choices with audience, generated date, and data date → user chooses one → **Present briefing**.

### 2. Find a saved template and generate with current data

Guide → user asks “Prepare the quarterly investment review for Horizon using current data” → guide proposes the best-matching approved template and explains the match in one sentence → user confirms or chooses **Show other templates** → guide shows the only missing consequential choices: portfolio/audience, as-of date, and material data caveat → **Generate briefing** → preparation message → completed briefing summary → **Open briefing**.

If the user asks only “Use the quarterly template,” the guide asks one compact clarification for the portfolio/audience rather than opening a settings form.

### 3. Create or modify a reusable template

Guide → user says “Create a template for monthly manager-watch meetings” or “Change the quarterly committee template to emphasize scenario risk” → guide reflects a concise proposed purpose, audience, sections, emphasis, and exclusions → **Preview template** → representative briefing preview → user requests a change in plain language or chooses **Save template** → saved confirmation.

When modifying, the guide first summarizes the proposed difference from the current template. It does not silently reinterpret or overwrite the template.

### 4. Review manager and portfolio alignment

Guide → user asks “Are we still aligned with Horizon’s objectives?” or selects the alignment suggestion → guide returns the overall conclusion, what changed, and the highest-priority exception → **Examine this exception** → focused explanation tied to the relevant manager/exposure and alignment dimension → **Review recommendation** → recommended discussion or decision → user can ask a follow-up or **Check next exception**.

The guide answers first; it does not begin by asking the user to choose a framework or analysis type.

### 5. Inspect deeper analytical evidence

From any guide answer or displayed briefing claim → user asks “Why?”, “Show the evidence,” or selects **View evidence** → guide opens an evidence response anchored to the exact claim, with values, time period, sources, and caveats → **Open analysis** for the full analytical view → **Back to answer** returns to the originating exchange.

The assistant never displays hidden chain-of-thought. “Why” returns inspectable evidence and a concise rationale.

### 6. Find and reopen a prior generated briefing

Guide → user asks in ordinary language, for example “Find the manager review we used with Horizon last spring” → guide returns up to a few likely briefings with the distinguishing client/audience, generated date, data date, and template → user chooses one → **Open briefing** → immutable historical briefing.

If nothing matches confidently, the guide asks for one high-value discriminator such as approximate date or audience. It does not present an advanced search form by default.

## State contract

| Focused state | Dominant action | Above the fold | Hidden unless requested |
|---|---|---|---|
| Guide entry | **Send request** | Current portfolio/client context, single request field, up to three personalized job examples | Feature navigation, templates list, report archive, system abilities catalog |
| Intent clarification | **Answer one question** | Guide’s understood objective, one consequential question, a few business-language choices if useful | Full configuration, prior conversation detail, technical constraints |
| Match/disambiguation | **Choose briefing/template** | At most a few matches with purpose/audience and dates | Long result set, relevance scores, IDs, query syntax |
| Generation proposal | **Generate briefing** | Proposed template, portfolio/audience, current-data date, material caveat | Prompt, model, source configuration, section micro-settings |
| Preparation response | **Open briefing** when ready | What is being prepared, business context, completion state | Agent/tool activity, queue/logs, fabricated precision |
| Completed briefing response after a preparation request | **Open briefing** | Title, executive conclusion, audience, dates, compact first-section preview | Presentation action as a peer, template construction, unrelated conversation, administration |
| Matched briefing response after a presentation request | **Present briefing** | Title, executive conclusion, audience, dates, compact first-section preview | Generation and editing, unrelated conversation, administration |
| Presentation | **Next** | Current content, progress, exit | Conversation, generation, authoring, navigation, system state |
| Template proposal | **Preview template** | Purpose, audience, sections, emphasis/exclusions, concise proposed changes | Prompt syntax, variables, bindings, model settings |
| Template preview/revision | **Save template** after requested changes are satisfied | Representative output, preview-data notice, concise difference summary | Renderer internals, field mappings, technical diff |
| Alignment answer | **Examine this exception** | Overall conclusion, what changed, top exception, as-of date | Full manager roster, frameworks menu, scoring mechanics |
| Exception answer | **Review recommendation** | Manager/exposure, alignment dimension, consequence, concise rationale | Other exceptions, full evidence corpus, raw calculations |
| Recommendation answer | **Check next exception** | Decision/discussion recommendation, urgency, remaining exception count; secondary return to summary | Task-management machinery, unrelated portfolio detail |
| Evidence response | **Back to answer** | Exact claim, key support/contradiction, values, period, sources, caveats; secondary access to full analysis | Chain-of-thought, retrieval metadata, raw source corpus |
| Detailed analysis | **Back to answer** | Requested analysis with assumptions and provenance in business terms | Queries, notebooks, pipelines, model traces |
| Historical-search response | **Open briefing** | Few best matches with client/audience and both dates | Archive tooling, technical versions, bulk actions |

The guide may accept free text in every conversational state, but the dominant action remains explicit and singular. Free text is not rendered as a competing primary control.

## What remains globally hidden

- feature map and implementation taxonomy;
- model or agent behavior and internal reasoning;
- full search result sets until the user asks to broaden;
- template configuration syntax;
- fully aligned managers and low-priority observations;
- raw analytical data and system provenance;
- administration and permissions.

## Strengths

- Fastest route when users can describe the outcome but do not know where it lives.
- Can collapse search, selection, and configuration into one understandable exchange.
- Handles ambiguous historical requests naturally by asking one useful question.
- Makes cross-domain questions such as “Why are we concerned, and should this change the client briefing?” feel coherent.
- Keeps technical structure almost entirely out of view.
- Can personalize starting points to role and current portfolio without creating a dashboard.

## Likely failure modes

- Users may not know what they can ask, especially for infrequent template-authoring jobs.
- Assistant interpretation can feel opaque; a plausible but wrong template or portfolio match is high risk.
- Repeated clarifying questions can become slower than direct selection.
- Conversation history can become cluttered and make stable artifacts hard to relocate.
- Template maintenance may lack the spatial overview needed to understand section order and completeness.
- Presenters may distrust an interface that appears generative unless the completed briefing’s fixed dates and immutability are unmistakable.
- The guide could become verbose, over-explain, or offer too many suggested actions, violating the calm one-action principle.

---

# Direction 3 — The Investment Library

## Architectural premise

Arangur is organized around durable business objects and their lifecycles. Users first locate the thing they want to act on, then enter a focused object state. The only top-level objects are Briefings, Templates, and managed Portfolios. Alignment is a current view of a portfolio, not a new saved object; evidence belongs to a claim, not to a separate evidence library.

## Entry point

A searchable investment library with three clearly separated collections: Briefings, Templates, and Portfolios. The default collection is chosen from role and recent behavior, but the user always sees which collection is active. The dominant entry action is **Find an item**.

Above the fold shows the active collection’s recent or relevant items with business metadata. It does not show summaries, charts, tasks, activity feeds, or mixed object cards.

## Object lifecycles

- **Briefing**: generated → available as a dated immutable document → presented/reopened → retained or archived under policy. Current-data regeneration creates another briefing.
- **Template**: draft → previewed → saved for reuse → modified with an understandable change summary → optionally retired by an authorized owner.
- **Portfolio**: already exists as a managed business entity → opened to current overview/alignment → reviewed at a stated as-of date. The UI does not create portfolios in these ordinary workflows.

## Exact interaction paths for the primary jobs

### 1. Open and present an already-generated briefing

Library → Briefings collection → search or select a recent briefing → **Open briefing** → briefing object page showing executive view and fixed dates → **Present** → presentation state → **Next** → **Exit presentation** → same briefing object page.

### 2. Find a saved template and generate with current data

Library → Templates collection → search/filter by audience, meeting, owner, or recent use → select template → **Open template** → template object page with purpose, audience, sections, and representative preview → **Use template** → choose portfolio/audience and confirm current-data date/readiness → **Generate briefing** → generated briefing object page.

The new briefing appears in the Briefings collection and records the originating template in ordinary metadata.

### 3. Create or modify a reusable template

Library → Templates collection → **New template** → focused template draft: purpose, audience, ordered meaningful sections, emphasis, exclusions → **Preview template** → representative preview → **Save template** → saved template object page.

To modify: Templates collection → open template → **Edit template** → focused edit state → **Preview changes** → changed representative preview → **Save changes** → same template object page with updated date and concise change summary.

Retirement, permissions, and version recovery are owner/admin actions hidden outside the default object page.

### 4. Review manager and portfolio alignment

Library → Portfolios collection → find/open portfolio → **Review alignment** → current portfolio alignment summary → **Inspect priority exception** → manager/exposure exception → **Review recommendation** → return to alignment summary or continue to next exception.

The portfolio object page shows the latest alignment conclusion and as-of date, not a grid of all analytics. The alignment view shows exceptions first and keeps aligned managers collapsed.

### 5. Inspect deeper analytical evidence

From a claim on a briefing object page or an alignment exception → **View evidence** → claim-bound evidence page/sheet → **Open analysis** if required → detailed analysis → **Back to claim** returns to the same object and position.

Evidence cannot be browsed as an independent collection because it has meaning only in relation to a claim and date.

### 6. Find and reopen a prior generated briefing

Library → Briefings collection → search by client, audience, meeting, generated date, data date, presenter, or originating template → results → select the intended item → **Open briefing** → immutable historical briefing object page.

From that page, “Create current briefing” is secondary and explicitly creates a new object from the same template and portfolio. It never alters the historical briefing.

## State contract

| Focused state | Dominant action | Above the fold | Hidden unless requested |
|---|---|---|---|
| Library/active collection | **Find an item** | Active collection name, search, recent/relevant objects with decisive metadata | Other collections’ content, dashboards, activity feed, analytics, admin |
| Briefings results | **Open briefing** | Title, client/audience, generated date, data date, template when distinguishing | Run IDs, status logs, storage details, bulk/archive controls |
| Briefing object page | **Present** | Title, audience, both dates, executive view, origin template as secondary metadata | Template internals, edit/regenerate controls, full sources, administration |
| Presentation | **Next** | Current content, discreet progress, exit | Library, metadata, authoring, generation, system state |
| Templates results | **Open template** | Name, purpose, audience, owner/approval if material, last used | Prompt/configuration, permissions detail, version internals |
| Template reuse object page | **Use template** | Purpose, audience, ordered sections, representative preview, updated date | Edit controls, prompt, bindings, models, internal versions, access administration |
| Template maintenance object page | **Edit template** | Purpose, audience, ordered sections, representative preview, updated date | Generation action, prompt, bindings, models, internal versions, access administration |
| New-template draft | **Preview template** | Purpose, audience, sections, emphasis/exclusions, unsaved status | Technical configuration, source IDs, advanced permissions |
| Existing-template edit | **Preview changes** | Purpose, audience, sections, emphasis/exclusions, unsaved status | Technical configuration, source IDs, advanced permissions |
| New-template preview | **Save template** | Representative output and preview-data label | Rendering controls, technical diff, generation internals |
| Template-change preview | **Save changes** | Representative output, preview-data label, concise change summary | Rendering controls, technical diff, generation internals |
| Use-template confirmation | **Generate briefing** | Selected template, portfolio/audience, data date/readiness, material caveat | Micro-configuration, model/source controls, execution details |
| Portfolios results | **Open portfolio** | Client/portfolio name, mandate descriptor, current data date, latest alignment conclusion | Every metric, managers roster, data diagnostics, administration |
| Portfolio object page | **Review alignment** | Portfolio/client, objectives/mandate synopsis, latest alignment conclusion and as-of date | Full analytics catalog, all managers, settings, raw holdings |
| Alignment summary | **Inspect priority exception** | Overall conclusion, change since last review, highest-priority exception | Aligned managers, full scoring matrix, calculation mechanics |
| Alignment exception | **Review recommendation** | Manager/exposure, dimension, consequence, evidence status | Other exceptions, full mandate/theme/scenario mappings |
| Recommendation | **Back to alignment** | Recommended discussion/decision, urgency, remaining exceptions; secondary access to next exception | Workflow automation, administrative assignment controls |
| Evidence summary | **Back to claim** | Exact claim, key values, period, sources, caveats; secondary access to full analysis | Unrelated evidence, raw records, system provenance |
| Detailed analysis | **Back to claim** | Requested analysis, assumptions, named sources, date | Query/pipeline mechanics, notebooks, hidden reasoning |

The active collection and entry intent create distinct focused states. Object pages do not accumulate an equal-weight action bar.

## What remains globally hidden

- mixed dashboards and cross-object activity feeds;
- independent evidence or analysis libraries;
- raw system objects and technical metadata;
- template construction machinery;
- scoring and scenario mechanics;
- administration, permissions, retention, and bulk operations;
- low-materiality alignment observations.

## Strengths

- Strongest discoverability and retrieval for known briefings, templates, and portfolios.
- Makes lifecycle distinctions concrete: template versus generated briefing versus managed portfolio.
- Historical reports remain easy to find and clearly immutable.
- Template ownership and reuse fit naturally without contaminating the reading experience.
- Predictable for users who prefer selecting a known business object before acting.
- Portfolio alignment has a stable home on the portfolio without becoming a separate invented object.

## Likely failure modes

- The library can become a dense filing system that makes users do more navigation before seeing value.
- Collections may encourage administrators to expose every backend object as a user-facing object.
- A global search and many filters can grow into technical metadata search.
- Cross-object jobs may feel fragmented—for example, reviewing alignment and then preparing a briefing from the findings.
- The portfolio object page could drift into a dashboard full of metrics and competing actions.
- Object metadata can crowd out actual briefing content if not aggressively constrained.
- Users who think in objectives rather than objects may struggle to choose the right collection.

## Review boundary

These directions are intentionally unresolved:

- **The Briefing Desk** optimizes for consuming and presenting finished output.
- **The Arangur Guide** optimizes for stating an objective and being guided to an answer.
- **The Investment Library** optimizes for locating and acting on durable business objects.

No direction is recommended or combined at this stage. Selection should occur only after review against the six user jobs and their minimum-success outcomes.
