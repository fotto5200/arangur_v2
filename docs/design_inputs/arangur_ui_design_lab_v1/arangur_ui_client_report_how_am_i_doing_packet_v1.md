# Arangur Client Report Design Packet v1

## “How am I doing?”

Status: Proposed communication contract and three storytelling directions for review
Scope: Client-facing report experience only
Not included: visual styling, final chart selection, mockups, advisor analysis screens, workflow setup, or implementation

## 1. Why this report exists

“How am I doing?” is the opening client question, not the name of a performance table. It asks whether the client’s wealth is doing what it is supposed to do, whether the result is sustainable, what materially changed, and what deserves discussion.

The report must support four client objective families:

1. **Return** — Is the portfolio earning the return expected for the capital and risk employed?
2. **Capital growth** — Are asset values and the client’s capital base appreciating as intended?
3. **Cash support** — Is the portfolio producing the cash the client needs without unexpected erosion of principal?
4. **Resilience** — Is the portfolio’s path still acceptable under the risks and stories that matter to the client?

These are capabilities, not four mandatory opening tiles. A client briefing promotes only the two or three objectives that define success for that client. A growth-oriented endowment might emphasize return, capital growth, and resilience; a family relying on distributions might emphasize return, cash support, and resilience.

A positive return alone cannot produce an “on track” conclusion. The conclusion requires the relevant client objective or required-return path and, where applicable, an expected capital-growth path, cash plan, and agreed risk boundary.

## 2. Communication contract

### Primary audience

A financially literate but nontechnical family-office principal, high-net-worth client, endowment representative, or similar asset owner receiving an advisor-led review.

### Secondary audience

A quantitatively sophisticated client who wants to verify the conclusion and inspect manager, lens, scenario, or attribution evidence without forcing that depth on everyone else.

### Immediate client objective

Within five minutes, understand:

- whether the portfolio is doing what it was intended to do;
- what the client received from it during the period;
- the most important reason the result occurred;
- the one issue, change, or decision that deserves attention now.

### Advisor’s immediate objective

Lead a confident, coherent conversation without translating a dense analytical screen in real time or exposing setup and calculation machinery.

### Minimum successful outcome

At the end of the opening report, the client can accurately say:

1. “My portfolio is ahead of, on, or behind its agreed path”—or “the system does not yet have enough objective data to say.”
2. “It earned this return, and this is how that compares with the return objective.”
3. “Its capital appreciated by this amount, while total assets changed by this amount after contributions and distributions.”
4. When cash support is a client objective: “It provided this amount of cash, and the next period appears covered or not covered.”
5. “This is the most important risk or concentration we should discuss, and the information is current as of this date.”

The client can ask “Why?” or “Show me” from any conclusion and reach its evidence in one action.

### The opening answer

The default opening should be a complete sentence that combines outcome and consequence. Using the supplied demonstration data, a provisional cash-oriented example is:

> The portfolio gained 7.8% and funded $1.1M of client cash needs; projected cash remains sufficient, while AI concentration is the principal risk to discuss.

A growth-oriented version should use the same sentence structure without forcing cash into equal prominence:

> The portfolio returned 7.8%; capital appreciation moved assets toward the agreed growth path, while AI concentration remains the principal risk to discuss.

The second sentence is a structural example, not a claim supported by the current fixture: validated dollar appreciation and the client’s growth path are not yet available. Either version may say “ahead of plan” or “on track” only after the relevant client objective is available.

### What must be visible immediately

- the conclusion in plain language;
- the measurement period and data as-of date;
- investment return against the client’s return objective—not merely against a benchmark;
- capital appreciation and total asset growth, clearly separated from external flows;
- cash delivered and near-term cash coverage when cash support is a client objective;
- one material watch item, if one exists;
- one dominant action that advances the presentation;
- discreet access to evidence for the visible claim.

### What remains hidden unless requested

- manager-level attribution;
- advisor-versus-manager attribution;
- full lens classifications;
- complete scenario lists;
- probabilistic assumptions and simulation mechanics;
- holdings and position-level calculations;
- exact benchmark decomposition;
- detailed methodology, definitions, and sources;
- all nonmaterial caveats;
- every metric that happens to be available.

### What never appears in the client report

- source template, workflow, run, job, or generation status;
- “confidence: mixed,” review-item counts, internal status labels, or synthetic-data plumbing;
- prompt, model, agent, API, connector, or calculation-pipeline terminology;
- edit, duplicate, delete, template, or data-loading controls;
- unexplained internal terms such as “lens bucket,” “row denominator,” or “residual/unexplained” on the opening level;
- a full-width analytical table as the first explanation of a conclusion.

### Material caveat policy

A caveat is visible on the client level only when it can change the client’s interpretation or decision. It is expressed in one direct sentence beside the affected conclusion. Definitions, secondary qualifications, and methodology live in details on demand. A disclaimer block is not allowed to compete with the report’s message.

### Presentation behavior

- One conclusion per presentation state.
- One visually dominant action: **Next** during the guided presentation.
- The advisor may open **Explain** or **Evidence** without losing the current place.
- Closing evidence returns to the exact originating conclusion.
- Presentation hides report-library, export, editing, and setup controls.
- Shared or printed versions preserve the narrative order but do not reproduce interaction chrome.

## 3. Evidence fixture for this design packet

The following realistic content comes from the supplied Northstar Family Office demonstration screens. It is sufficient to make the directions concrete but is not a final client-data specification.

### Directly supplied or directly derived

- Data as of June 30, 2026.
- Current portfolio value: approximately **$44.9M**, derived from the stated post-scenario values and impacts.
- Weighted portfolio return: approximately **7.79%**, derived from the manager weights and returns shown.
- Global policy benchmark: **6.99%**.
- Difference versus global policy benchmark: approximately **+0.80 percentage points**.
- Cash generated during the period: **$1.4M**.
- Cash paid out: **$1.1M**.
- Cash retained/reinvested: **$255K**.
- Stated next-period annual cash need: **$1.2M**.
- Projected next-period generation: approximately **$1.3M**.
- Projected surplus versus need: **$115K**.
- AI / Chip Selloff deterministic scenario: **-$9.5M / -21.1%**, leaving **$35.4M**.
- Rate Shock deterministic scenario: **-$4.8M / -10.7%**, leaving **$40.1M**.
- Advisor policy effect before manager implementation: **-0.26 percentage points**.
- Manager implementation effect: **+1.05 percentage points**.
- Net decision effect versus the global policy basis: approximately **+0.79 percentage points**.
- AI Adoption lens: **10.5%** of the portfolio is in an unclassified/review-required bucket.

### Missing before a report may claim “on track”

- the client’s wealth objective or required-return path;
- the client’s desired capital-growth path, if distinct from the return objective;
- treatment of inflation, taxes, fees, contributions, and withdrawals in that objective;
- agreed cash horizon and minimum coverage standard;
- agreed loss tolerance or scenario boundary;
- validated period-start value and capital-flow reconciliation;
- which benchmark, if any, is appropriate for client-facing comparison.

The absence of these fields is a product requirement, not a reason to add explanatory UI. Until they exist, the report uses precise outcome language and does not manufacture a plan-status conclusion.

### Measurement rules for return and growth

The report must not use return, capital appreciation, and asset growth as synonyms.

- **Investment return** is flow-adjusted percentage performance over a stated period. The approved calculation convention must be consistent and available at verification depth.
- **Capital appreciation** is the dollar or percentage increase in asset values attributable to realized and unrealized valuation change, excluding external contributions and client withdrawals. Income is separated when the selected return convention requires it.
- **Total asset growth** is the change from opening to ending portfolio value after investment results, contributions, withdrawals, distributions, fees, and other flows are reconciled. It is a balance-sheet change, not automatically an investment-performance measure.
- **Cash support** is cash made available or paid to the client. It is not assumed to equal investment income and is not shown as unexplained asset loss.

Simple client language may include:

- “Public equities returned X% during the period.”
- “Private investments doubled in estimated value over 18 months; most of the increase remains unrealized.”
- “Total assets grew from $A to $B after $C was distributed.”

Each statement opens to a precise definition and reconciliation. Illiquid-asset appreciation always discloses the valuation date and whether the change is realized or estimated.

## 4. Shared depth model

Every direction uses three depths. The client never has to choose a “mode.” Depth follows the question being asked.

### Depth 1 — Understand

The five-minute presentation. One conclusion, one meaningful visual relationship, and no more than three primary figures in a state.

### Depth 2 — Explain

A concise breakdown answering “What drove that?” or “What does that include?” It adds one layer of comparison, composition, or time—not a raw table.

### Depth 3 — Verify

The analytical evidence: exact values, assumptions, sources, methodology, position-level calculation results, and tables where tables are genuinely the clearest verification format.

The path is always:

**Conclusion → Explain → Verify → Back to the same conclusion**

## 5. Direction A — The Plan Check

### Storytelling premise

Organize the report around the objectives that define success for the client. Return, capital growth, cash support, and resilience are available objective families, but only the two or three relevant to the client appear in the opening. The report answers “How am I doing?” as a goal-status question.

### Opening message

> Results were positive and cash needs were funded. The portfolio’s AI concentration is the item that may place the agreed risk path under pressure.

When objective data is available, the first sentence becomes a true status judgment such as “The portfolio remains on plan, with one risk outside the agreed review boundary.”

### Five-minute presentation path

#### State A1 — Overall plan check

- **Client question:** Am I on track?
- **Visible:** one conclusion and no more than three active objectives; a growth-led example uses Return, Capital Growth, and Resilience, while a distribution-led example uses Return, Cash Support, and Resilience; period and as-of date.
- **Illustrative content:** 7.79% portfolio result; capital-growth status when reconciliation data exists or $1.1M paid when cash is the selected objective; AI / Chip Selloff as the principal modeled downside.
- **Dominant action:** **See what changed**.
- **Hidden:** benchmark decomposition, all managers, complete scenarios, exact lens buckets.

#### State A2 — Return and capital growth

- **Client question:** Did my investments perform, and did my capital grow as intended?
- **Visible:** flow-adjusted return against the client’s required return; dollar capital appreciation; reconciled opening-to-ending asset growth; a direct statement of ahead/on/behind or “objective not yet recorded.”
- **Interim evidence:** 7.79% outcome versus 6.99% global policy benchmark, clearly labeled as benchmark context rather than the client objective. Dollar appreciation remains unavailable until capital flows and valuation changes are reconciled.
- **Dominant action:** **Review next objective**.
- **Hidden:** manager attribution, advisor attribution, holdings, benchmark construction.

The next objective is fixed by the client’s reporting philosophy before the briefing is generated. A growth-led briefing moves directly to Resilience; a distribution-led briefing includes Cash Support. The client is not asked to configure this during presentation.

#### State A3 — Support

- **Client question:** Did the portfolio provide what I needed, and can it continue?
- **Visible:** $1.1M paid during the period; $1.3M projected generation versus $1.2M need; $115K projected cushion.
- **Visual relationship:** required cash and expected cash on the same scale, with the cushion directly labeled.
- **Dominant action:** **Review resilience**.
- **Hidden:** cash source-by-source detail, sleeve cash flows, model mechanics.

#### State A4 — Resilience

- **Client question:** What could knock the plan off course?
- **Visible:** current value and the one principal downside on the same value scale; AI / Chip Selloff moves $44.9M to $35.4M; the agreed tolerance boundary when available.
- **Dominant action:** **Discuss the priority**.
- **Hidden:** the scenario catalog, probability mechanics, every lesser scenario, holdings-level losses.

#### State A5 — Discussion close

- **Client question:** What should we discuss or decide?
- **Visible:** one recommendation or open question tied to the concentration; confirmation of what remains on plan; next review trigger.
- **Dominant action:** **Finish briefing**.
- **Hidden:** task-management and workflow machinery.

### Explain and verify paths

- Return and capital growth → **Explain growth** → return, appreciation, income, and external-flow reconciliation → **View performance evidence** → asset-class and holding-level results. Attribution remains a separate optional explanation.
- Support → **Explain cash** → generated, paid, and retained relationship → **View cash evidence** → exact periods and sources.
- Resilience → **Compare scenarios** → selected deterministic and probabilistic cases on one stable value scale → **View scenario evidence** → position-level before/after valuation and assumptions.

### Visual logic to explore after direction selection

- A single goal path with no more than three active objectives, not a four-card dashboard.
- Direct comparison to thresholds and objectives; no gauges or decorative scores.
- Scenario outcomes placed on one stable value axis so magnitude remains comparable.
- Probabilistic results shown as ranges around outcomes, never as false-certainty point forecasts.

### Appropriate animation

The plan state may transition from the prior review to the current review, revealing only what changed. Scenario comparison may move the same portfolio marker along a fixed value axis. Animation explains a change; it does not continuously pulse, count, or decorate.

### Strengths

- Answers the client’s actual objective rather than equating performance with success.
- Balances growth, cash, and risk without requiring the client to assemble the answer.
- Creates a repeatable structure across family offices, individuals, and institutions.
- Makes exceptions prominent while allowing healthy dimensions to remain quiet.
- Strong fit for concise recurring reviews.

### Likely failure modes

- Can become a generic scorecard if the active objectives are rendered as independent cards.
- A red/amber/green shorthand can hide magnitude and nuance.
- Requires well-defined client objectives; without them, “on track” becomes misleading.
- May under-explain who or what produced the result.
- Too many client objectives would destroy the opening simplicity; relevant does not mean simultaneous.

## 6. Direction B — The Wealth Journey

### Storytelling premise

Organize the report through time: where the client began, what changed the portfolio, where it stands now, and the range of plausible paths ahead. The report answers “How am I doing?” as a progression question.

### Opening message

> Your portfolio returned 7.8% and ended the period at approximately $44.9M after supporting $1.1M of cash payments. The widest material downside comes from the AI / Chip Selloff scenario.

### Five-minute presentation path

#### State B1 — The period in one journey

- **Client question:** Where did I start, and where am I now?
- **Visible:** reconciled starting value, flow-adjusted return, dollar capital appreciation, external additions/withdrawals, client payments, and ending value as one continuous story; period and as-of date. Only the three figures most important to the narrative are promoted.
- **Dominant action:** **Follow the journey**.
- **Hidden:** manager breakdown, transaction detail, exact calculation ledger.

The current fixture does not contain a validated start-value/capital-flow reconciliation. That data must be present before this direction can be mocked up faithfully.

#### State B2 — What moved the path

- **Client question:** What mattered during the period?
- **Visible:** no more than three material movements, expressed in client terms—for example public-equity return, private-asset appreciation, and cash paid. A growth-led client may instead see return, capital appreciation, and net asset growth.
- **Dominant action:** **Look ahead**.
- **Hidden:** full attribution matrix, nonmaterial movements, manager roster.

#### State B3 — Forward objective path

- **Client question:** Can the result that matters to me continue?
- **Visible:** the selected objective on one time axis. A growth-led briefing shows actual return/capital growth against the forward required path. A distribution-led briefing shows historical cash delivered and projected $1.3M generation against $1.2M need, with the $115K cushion directly labeled.
- **Dominant action:** **Test the path**.
- **Hidden:** secondary objectives, cash-source or return decomposition, and distant forecasts.

#### State B4 — Range of futures

- **Client question:** How different could the path become?
- **Visible:** base path, probabilistic range when available, and selected deterministic events on a consistent portfolio-value axis; current $44.9M, Rate Shock $40.1M, and AI / Chip Selloff $35.4M.
- **Dominant action:** **Discuss the path**.
- **Hidden:** long scenario catalog, simulation internals, position table.

#### State B5 — Discussion close

- **Client question:** What should change, if anything?
- **Visible:** the advisor’s conclusion about whether the path remains acceptable and one proposed response or monitoring trigger.
- **Dominant action:** **Finish briefing**.
- **Hidden:** implementation workflow and order-entry concepts.

### Explain and verify paths

- Period journey → **Explain change** → contribution/withdrawal/investment bridge → **Verify reconciliation** → exact ledger.
- Material movement → **Explain driver** → advisor/manager/market contribution at a suitable level → **View attribution evidence** → analytical matrices.
- Range of futures → **Explain range** → named scenario assumptions and percentile meaning → **Verify valuation** → position-level before/after results.

### Visual logic to explore after direction selection

- A continuous path or bridge rather than separate metric cards.
- Past, present, and future are visually distinct; forecasts never look like observed history.
- Deterministic scenarios branch from the same present point.
- Probabilistic boundaries use the same scale and horizon as deterministic comparisons when comparison is valid.
- Cash distributions and capital growth appear as parts of the wealth journey, with the client’s selected objective controlling emphasis.

### Appropriate animation

The portfolio moves from opening value through the period’s few material changes to ending value. The forward range then grows from the current point; deterministic scenarios branch only when the advisor invokes them. Motion may be paused or replayed and is replaced by static sequencing in exports.

### Strengths

- Naturally understandable to clients who think in “what happened to my wealth?” terms.
- Makes withdrawals and cash support part of the outcome rather than an apparent performance failure.
- Makes percentage return, dollar appreciation, and total asset growth understandable without conflating them.
- Handles evolution, changes since last review, and forward scenarios well.
- Provides meaningful uses for animation.
- Can integrate historical observation and forward-looking risk without pretending they are the same.

### Likely failure modes

- Can imply more forecast precision than exists, especially with probabilistic ranges.
- A long time horizon or many cash flows can make the journey visually complex.
- May bury the client’s explicit objective unless the plan path is always present.
- Can understate who made the decisions behind the outcome.
- Requires excellent capital-flow reconciliation; incorrect or incomplete flow data breaks trust immediately.

## 7. Direction C — The Stewardship Brief

### Storytelling premise

Organize the report around accountability: what the portfolio delivered, which decisions added or detracted from the result, what the advisor and managers are watching, and what action is proposed. The report answers “How am I doing?” as a stewardship question.

### Opening message

> The portfolio returned 7.8% and ended at approximately $44.9M. Manager implementation added value overall, while the advisor-level policy effect detracted modestly; AI concentration is the forward issue to address.

### Five-minute presentation path

#### State C1 — Client outcome

- **Client question:** What did my portfolio deliver to me?
- **Visible:** no more than three client outcomes. A growth-led example uses 7.79% return, validated dollar appreciation, and approximate ending value $44.9M. A distribution-led example replaces dollar appreciation with $1.1M cash paid. One sentence states whether the relevant client objectives were met when available.
- **Dominant action:** **See what drove it**.
- **Hidden:** detailed attribution categories, benchmarks, managers, scenarios.

#### State C2 — Stewardship contribution

- **Client question:** Where did value come from?
- **Visible:** one clear relationship between advisor policy decisions, manager implementation, and total outcome versus the agreed comparison basis; illustrative effects of -0.26 percentage points and +1.05 percentage points, net +0.79.
- **Dominant action:** **See what matters next**.
- **Hidden:** six-manager matrix, mandate sub-benchmark selection/sizing, asset selection/sizing, residuals.

The language must describe decision responsibility without turning the presentation into a scorekeeping or blame exercise.

#### State C3 — The manager story

- **Client question:** Is there a manager decision I should understand?
- **Visible:** only the most material manager contribution or concern, with consequence and advisor interpretation.
- **Dominant action:** **Review the forward issue**.
- **Hidden:** managers within tolerance, full attribution matrix, small effects.

#### State C4 — Forward stewardship

- **Client question:** What is the team watching or proposing?
- **Visible:** AI concentration as the main issue; $9.5M / 21.1% deterministic downside; any proposed advisor allocation or manager-philosophy change, shown with its impact before it is implemented.
- **Dominant action:** **Discuss the recommendation**.
- **Hidden:** scenario catalog, trade lists, holdings, implementation controls.

#### State C5 — Discussion close

- **Client question:** What decision or follow-up is required from me?
- **Visible:** one recommendation, why it is consistent with the client objective, and what would cause the team to revisit it.
- **Dominant action:** **Finish briefing**.
- **Hidden:** internal approval and execution workflow.

### Explain and verify paths

- Stewardship contribution → **Explain responsibilities** → plain-language advisor-versus-manager attribution → **View attribution evidence** → exact benchmark and decision-category matrix.
- Manager story → **Explain manager result** → mandate selection, sizing, asset selection, and sizing at a summarized level → **Verify analysis** → full manager report.
- Forward issue → **Explain proposed response** → before/after portfolio and scenario comparison → **Verify impact** → position-level revaluation.

### Visual logic to explore after direction selection

- A causal chain from decisions to portfolio result to client consequence.
- Attribution displayed as a small number of additive contributions, not a wide matrix.
- Responsibility separated clearly: client objective, advisor policy/allocation, manager implementation, market outcome.
- Proposed changes shown as before/after comparisons and never mixed with current holdings.

### Appropriate animation

Decision contributions may assemble into the total result in a fixed sequence. A proposed change may transition the current portfolio into a clearly labeled hypothetical portfolio, then compare both under the same scenario. Animation must make causality or change legible, not dramatize performance.

### Strengths

- Demonstrates what the advisor and managers actually contributed.
- Strong fit for family offices, endowments, boards, and governance-oriented clients.
- Connects historical outcome to forward action.
- Makes proposed changes understandable before implementation.
- Provides a disciplined route from a client-level conclusion to sophisticated attribution evidence.

### Likely failure modes

- Can feel self-justifying if advisor value is emphasized more than client outcomes.
- Attribution language can become technical very quickly.
- Responsibility categories can be mistaken for blame.
- May overwhelm a client who only wants the five-minute answer.
- The opening could drift toward advisor analysis rather than client communication.

## 8. Direction comparison

| Evaluation question | The Plan Check | The Wealth Journey | The Stewardship Brief |
|---|---|---|---|
| Primary organizing question | Are my objectives being met? | How did my wealth move, and where could it go? | What did my team deliver and decide? |
| Best first impression | Clear status and exception | Intuitive progression through time | Accountability and active stewardship |
| Natural visual relationship | Outcome versus objective/threshold | Past-to-present bridge and forward range | Decision contributions and causal chain |
| Best fit | Recurring concise client review | Clients focused on wealth evolution and scenarios | Governance-oriented or analytically engaged clients |
| Main dependency | Explicit client objectives | Reconciled capital flows and history | Trustworthy decision attribution |
| Main risk | Generic scorecard | False forecast precision | Technical or self-serving tone |

This table is for evaluation only. It does not authorize combining the directions.

## 9. Simplification gate before mockups

Any selected direction must pass all of the following before visual design begins:

- The opening conclusion can be understood without reading a legend.
- No presentation state contains more than one conclusion.
- No presentation state promotes more than three primary figures.
- Every figure supports the visible conclusion; availability is not sufficient reason to show it.
- Return, capital appreciation, total asset growth, and cash support never appear as four undifferentiated peer metrics.
- Asset growth is never presented as investment return; external flows are reconciled.
- Illiquid-asset appreciation identifies the valuation date and whether the increase is realized or estimated.
- The portfolio is compared with the client objective before a market or policy benchmark.
- Cash paid is not presented as unexplained portfolio loss.
- Deterministic and probabilistic results are labeled as different forms of evidence.
- Scenario values intended for comparison use a consistent scale, horizon, and portfolio base.
- A table appears only at verification depth or when exact cross-row comparison is the client’s actual task.
- Technical definitions do not appear as permanent explanatory paragraphs.
- Material caveats are visible, concise, and adjacent to the affected claim.
- Details are accessible by click/tap as well as hover.
- Animation can be paused, survives as a meaningful static sequence, and communicates change or causality.
- The advisor can answer an unexpected “Why?” and return to the same presentation position.
- Client presentation contains no template, generation, data-loading, export, or administrative controls.

## 10. Prototype acceptance scripts for the eventual selected direction

These are not prototype results. They define what the later prototype must prove.

### Script 1 — Five-minute client

The advisor presents the report without opening evidence. The client must correctly identify the overall outcome, cash position, principal watch item, and as-of date.

### Script 2 — Sophisticated client asks why

From the visible performance conclusion, the advisor opens one explanatory layer, then exact attribution evidence, and returns to the same place without restarting the presentation.

### Script 3 — Scenario question

The client asks how a Rate Shock compares with an AI / Chip Selloff and with the probabilistic range. The advisor compares them on a consistent base and scale without opening a scenario catalog or explaining simulation plumbing.

### Script 4 — Cash concern

The client asks whether distributions are eroding principal. The report distinguishes investment result, cash generated, cash paid, retained cash, and portfolio-value change without requiring a raw transaction table.

### Script 5 — Historical integrity

The client asks whether the numbers have changed since the briefing was prepared. The advisor can identify the report’s fixed as-of date and explain that a current-data version would be a new briefing.

## Review decision

Select one storytelling premise for visual exploration:

- **The Plan Check** — objectives and thresholds;
- **The Wealth Journey** — progression through time;
- **The Stewardship Brief** — decisions and accountability.

The next approved step is to create three visual concepts within the selected storytelling direction. No direction is selected or blended in this packet.
