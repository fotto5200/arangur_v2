# Manager Role Review v1

## Purpose

Manager role review answers a practical advisor question:

```text
Why do we own this manager?
```

The first required path is:

```text
Why do we own Manager 5?
```

The point is not to rank or fire managers automatically. The point is to make role, mandate, overlap, diversification value, and scenario usefulness visible enough for an advisor to have a responsible conversation.

## Manager Role / Mandate Framing

A manager should have an intended role. Examples:

- Core public equity exposure.
- Diversifying satellite exposure.
- Defensive income.
- Private-market growth.
- Inflation sensitivity.
- Liquidity reserve.
- Opportunistic risk.
- Thematic exposure.

The role can be advisor-defined, client-agreed, or inferred temporarily for demo purposes. Client-facing output should distinguish known mandate metadata from inferred evidence.

## Category, Theme, And Macro Exposure Comparison

Advisor and client may care about specific categories:

- Sector exposure.
- Theme exposure.
- Macro concern exposure.
- Mandate bucket.
- Growth/value/quality framing.
- Liquidity role.
- Scenario sensitivity.

A manager-role view can compare each manager across those agreed categories. This is more useful than asking whether holdings overlap in the abstract. It asks whether two managers are doing the same job in the terms the client and advisor actually care about.

## Overlap And Shadowing Logic

Shadowing means one manager closely resembles another manager across the categories that matter.

Possible red flags:

- Similar top holdings.
- Similar theme and sector exposure.
- Similar scenario behavior.
- Similar mandate bucket.
- Similar role in client language.
- Similar downside under the scenarios used in the briefing.

If Manager 5 is closely shadowed by another manager, the system should flag a role question:

```text
Manager 5 appears similar to another manager across the categories selected for this briefing. Is this duplication intentional, or was Manager 5 expected to do something different?
```

## Intentional Versus Accidental Duplication

Duplication is not automatically bad.

Intentional duplication may be appropriate when:

- The advisor wants to reinforce a thesis.
- Two managers use different implementation styles.
- A client has requested deliberate concentration.
- One manager provides liquidity or access that another does not.
- The mandate explicitly calls for similar exposure.

Accidental duplication may be a problem when:

- The manager was hired for diversification but mirrors another manager.
- The overlap increases concentration without clear client agreement.
- Scenario usefulness is redundant.
- The manager's role has drifted from the original thesis.

## Manager Role Evidence Cards

Minimum evidence cards:

- Manager allocation.
- Intended role or mandate, if known.
- Top exposures.
- Similar managers / shadowing candidates.
- Direct overlap.
- Scenario usefulness.
- Data confidence and verification needs.

## Current Demo Support

Current demo can support:

- Manager/account allocation.
- Top holdings.
- Sector and theme exposure from synthetic fixture tags.
- Direct holding overlap.
- Deterministic scenario impact.
- Data confidence and human-review counts.

Current demo does not yet support:

- Explicit manager mandate.
- Intended role.
- Expected diversification contribution.
- Manager thesis.
- Benchmark/context frame.
- Fund look-through.
- Real client-agreed categories.

## Metadata Needed Later

Future manager-role review may need:

- Manager mandate.
- Intended role.
- Expected diversification contribution.
- Expected scenario usefulness.
- Manager thesis.
- Benchmark/context frame.
- Client/advisor category set.
- Manager role history.
- Review status and advisor notes.

## Caveats And Do-Not-Overclaim Language

Use language like:

```text
This evidence raises a manager-role question.
```

Avoid language like:

```text
This manager should be removed.
```

The system should frame overlap and shadowing as evidence for advisor review. It should not make autonomous investment recommendations.
