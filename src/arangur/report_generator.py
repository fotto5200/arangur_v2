"""Generate advisor-readable Markdown and HTML reports for the local demo."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


DEMO_CAVEAT = (
    "Demo only: this report uses synthetic data and local fixture prices. It is intended to "
    "demonstrate Arangur v2 product behavior and is not investment advice, a client statement, "
    "or a production valuation."
)


def generate_markdown_report(
    snapshot: dict[str, Any],
    valuation: dict[str, Any],
    exposure_overlap: dict[str, Any],
    scenario_result_set: dict[str, Any],
    output_path: Path,
    workflow_template: dict[str, Any] | None = None,
    data_coverage_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate the demo Markdown report plus a simple HTML companion."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = output_path.with_suffix(".html")
    context = _build_report_context(
        snapshot,
        valuation,
        exposure_overlap,
        scenario_result_set,
        workflow_template,
        data_coverage_result,
    )

    output_path.write_text(_render_markdown(context), encoding="utf-8")
    html_path.write_text(_render_html(context), encoding="utf-8")

    return {
        "schema_version": "report_package.v1",
        "report_id": "arangur_demo_report",
        "report_title": context["title"],
        "valuation_date": snapshot["as_of_date"],
        "portfolio_id": snapshot["portfolio"]["portfolio_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "is_synthetic": snapshot["portfolio"]["is_synthetic"],
        "audience": "advisor_colleague_demo",
        "outputs": [
            {"format": "markdown", "path": _stable_output_path(output_path)},
            {"format": "html", "path": _stable_output_path(html_path)},
        ],
    }


def _build_report_context(
    snapshot: dict[str, Any],
    valuation: dict[str, Any],
    exposure_overlap: dict[str, Any],
    scenario_result_set: dict[str, Any],
    workflow_template: dict[str, Any] | None = None,
    data_coverage_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    total_value = valuation["portfolio_total"]["market_value"]
    cash_value = valuation["portfolio_total"]["cash_value"]
    primary_scenario = scenario_result_set["scenario_results"][0]
    top_theme = exposure_overlap["exposures"]["by_theme"][0]
    top_sector = exposure_overlap["exposures"]["by_sector"][0]
    largest_overlap = exposure_overlap["overlaps"][0] if exposure_overlap["overlaps"] else None
    workflow = workflow_template or _default_workflow_template()

    return {
        "title": f"{snapshot['portfolio']['portfolio_name']} Review",
        "portfolio_owner": snapshot["portfolio"]["owner_label"],
        "advisor_label": snapshot["portfolio"].get("advisor_label") or "N/A",
        "valuation_date": snapshot["as_of_date"],
        "total_value": total_value,
        "cash_value": cash_value,
        "cash_percent": _ratio(cash_value, total_value),
        "manager_rows": [
            [row["manager_name"], _currency(row["market_value"]), _percent(row["market_value"], total_value)]
            for row in valuation["manager_totals"]
        ],
        "account_rows": [
            [row["account_name"], row["manager_name"], _currency(row["market_value"]), _currency(row["cash_value"])]
            for row in valuation["account_totals"]
        ],
        "top_holding_rows": [
            [
                row["display_name"],
                row.get("ticker") or "",
                row["manager_name"],
                _currency(row["market_value"]),
                _percent(row["market_value"], total_value),
            ]
            for row in exposure_overlap["top_holdings"][:10]
        ],
        "sector_rows": _exposure_rows(exposure_overlap["exposures"]["by_sector"][:10]),
        "theme_rows": _exposure_rows(exposure_overlap["exposures"]["by_theme"][:12]),
        "overlap_rows": _overlap_rows(exposure_overlap["overlaps"][:10]),
        "scenario_rows": [
            [
                scenario["scenario_name"],
                _currency(scenario["portfolio_before_value"]),
                _currency(scenario["portfolio_after_value"]),
                _currency(scenario["portfolio_impact_value"]),
                _percent_value(scenario["portfolio_impact_percent"]),
            ]
            for scenario in scenario_result_set["scenario_results"]
        ],
        "primary_scenario": primary_scenario,
        "scenario_impact_rows": [
            [
                row["display_name"],
                row.get("ticker") or "",
                row["matched_rule"],
                _currency(row["before_value"]),
                _currency(row["impact_value"]),
            ]
            for row in sorted(primary_scenario["position_impacts"], key=lambda item: item["impact_value"])[:8]
        ],
        "executive_summary": [
            f"The synthetic Northstar portfolio totals {_currency(total_value)} across {len(valuation['manager_totals'])} managers and {len(valuation['account_totals'])} accounts.",
            f"Cash and cash-like reserves are {_currency(cash_value)}, or {_percent_value(_ratio(cash_value, total_value))} of the portfolio.",
            f"The largest supplied theme exposure is {top_theme['bucket_label']} at {_percent_value(top_theme['portfolio_percent'])}; the largest sector exposure is {top_sector['bucket_label']} at {_percent_value(top_sector['portfolio_percent'])}.",
            _overlap_summary(largest_overlap),
            f"The primary scenario, {primary_scenario['scenario_name']}, shows an illustrative {_currency(primary_scenario['portfolio_impact_value'])} impact ({_percent_value(primary_scenario['portfolio_impact_percent'])}).",
        ],
        "workflow": workflow,
        "workflow_focus": [
            f"Workflow: {workflow['display_name']} ({workflow['workflow_type']})",
            f"Audience: {workflow['intended_audience']}",
            f"Meeting goal: {workflow['meeting_goal']}",
        ],
        "workflow_primary_questions": workflow["primary_questions"],
        "workflow_emphasized_sections": workflow["emphasized_report_sections"],
        "workflow_de_emphasized_sections": workflow.get("de_emphasized_sections", []),
        "workflow_required_inputs": workflow["required_inputs"],
        "workflow_talking_points": workflow["advisor_talking_points"],
        "workflow_caveats": workflow["caveats"],
        "workflow_follow_up_actions": workflow["suggested_follow_up_actions"],
        "workflow_next_upgrade_path": workflow["next_upgrade_path"],
        "data_coverage": _data_coverage_context(data_coverage_result, workflow),
    }


def _render_markdown(context: dict[str, Any]) -> str:
    primary = context["primary_scenario"]
    lines = [
        f"# {context['title']}",
        "",
        "## Synthetic-Data Caveat",
        "",
        DEMO_CAVEAT,
        "",
        "## Workflow Focus",
        "",
        *_bullets(context["workflow_focus"]),
        "",
        "### Primary Questions",
        "",
        *_bullets(context["workflow_primary_questions"]),
        "",
        "### Emphasized Report Sections",
        "",
        *_bullets(context["workflow_emphasized_sections"]),
        "",
        *_markdown_data_coverage_section(context["data_coverage"]),
        "",
        "## Executive Summary",
        "",
        *_bullets(context["executive_summary"]),
        "",
        "## Portfolio Value Summary",
        "",
        *_bullets(
            [
                f"Portfolio: {context['portfolio_owner']}",
                f"Advisor label: {context['advisor_label']}",
                f"Valuation date: {context['valuation_date']}",
                f"Total value: {_currency(context['total_value'])}",
                f"Cash: {_currency(context['cash_value'])} ({_percent_value(context['cash_percent'])})",
            ]
        ),
        "",
        "## Manager/Account Summary",
        "",
        "### Manager Summary",
        "",
        _markdown_table(["Manager", "Market Value", "Portfolio %"], context["manager_rows"]),
        "",
        "### Account Summary",
        "",
        _markdown_table(["Account", "Manager", "Market Value", "Cash"], context["account_rows"]),
        "",
        "## Top Holdings",
        "",
        _markdown_table(["Holding", "Ticker", "Manager", "Market Value", "Portfolio %"], context["top_holding_rows"]),
        "",
        "## Sector Exposure",
        "",
        _markdown_table(["Sector", "Market Value", "Portfolio %"], context["sector_rows"]),
        "",
        "## Theme Exposure",
        "",
        "Theme exposure can exceed 100% in aggregate because a security can carry multiple theme tags.",
        "",
        _markdown_table(["Theme", "Market Value", "Portfolio %"], context["theme_rows"]),
        "",
        "## Manager Overlap / Duplication Findings",
        "",
        _markdown_overlap_section(context["overlap_rows"]),
        "",
        "## Scenario Shock Summary",
        "",
        "Scenario shocks are deterministic demo approximations, not forecasts.",
        "",
        _markdown_table(["Scenario", "Before", "After", "Impact", "Impact %"], context["scenario_rows"]),
        "",
        f"Primary scenario detail: **{primary['scenario_name']}**",
        "",
        primary["description"],
        "",
        _markdown_table(["Holding", "Ticker", "Matched Rule", "Before", "Impact"], context["scenario_impact_rows"]),
        "",
        "## Advisor Talking Points",
        "",
        *_bullets(context["workflow_talking_points"]),
        "",
        "## Suggested Follow-Up Actions",
        "",
        *_bullets(context["workflow_follow_up_actions"]),
        "",
        "## Workflow Caveats",
        "",
        *_bullets(context["workflow_caveats"]),
        "",
        "## What This Demo Proves",
        "",
        *_bullets(
            [
                "Arangur v2 can run a complete local portfolio-analysis loop from synthetic fixtures.",
                "The canonical snapshot can feed valuation, exposure, overlap, scenario, and report generation without source-specific coupling.",
                "The report can explain holdings, overlap, and scenario impact in advisor-readable language.",
            ]
        ),
        "",
        "## What This Demo Does Not Yet Prove",
        "",
        *_bullets(
            [
                "It does not prove live ingestion, Plaid integration, custodian reconciliation, market-data vendor integration, or production data quality.",
                "It does not implement tax lots, FX, shorts, derivatives, fees, corporate actions, performance attribution, or advanced accounting.",
                "It does not use or validate legacy MATLAB logic.",
            ]
        ),
        "",
        "## Next Planned Upgrades",
        "",
        *_bullets(
            [
                context["workflow_next_upgrade_path"],
                "Add stronger validation edge cases and report-quality tests around malformed local fixtures.",
                "Design the future Plaid Sandbox boundary without committing credentials or using real client data.",
            ]
        ),
        "",
    ]
    return "\n".join(lines)


def _render_html(context: dict[str, Any]) -> str:
    primary = context["primary_scenario"]
    sections = [
        _html_section("Synthetic-Data Caveat", f"<p class=\"caveat\">{escape(DEMO_CAVEAT)}</p>"),
        _html_section(
            "Workflow Focus",
            _html_list(context["workflow_focus"])
            + "<h3>Primary Questions</h3>"
            + _html_list(context["workflow_primary_questions"])
            + "<h3>Emphasized Report Sections</h3>"
            + _html_list(context["workflow_emphasized_sections"]),
        ),
        _html_data_coverage_section(context["data_coverage"]),
        _html_section("Executive Summary", _html_list(context["executive_summary"])),
        _html_section(
            "Portfolio Value Summary",
            _html_list(
                [
                    f"Portfolio: {context['portfolio_owner']}",
                    f"Advisor label: {context['advisor_label']}",
                    f"Valuation date: {context['valuation_date']}",
                    f"Total value: {_currency(context['total_value'])}",
                    f"Cash: {_currency(context['cash_value'])} ({_percent_value(context['cash_percent'])})",
                ]
            ),
        ),
        _html_section(
            "Manager/Account Summary",
            "<h3>Manager Summary</h3>"
            + _html_table(["Manager", "Market Value", "Portfolio %"], context["manager_rows"])
            + "<h3>Account Summary</h3>"
            + _html_table(["Account", "Manager", "Market Value", "Cash"], context["account_rows"]),
        ),
        _html_section("Top Holdings", _html_table(["Holding", "Ticker", "Manager", "Market Value", "Portfolio %"], context["top_holding_rows"])),
        _html_section("Sector Exposure", _html_table(["Sector", "Market Value", "Portfolio %"], context["sector_rows"])),
        _html_section(
            "Theme Exposure",
            "<p>Theme exposure can exceed 100% in aggregate because a security can carry multiple theme tags.</p>"
            + _html_table(["Theme", "Market Value", "Portfolio %"], context["theme_rows"]),
        ),
        _html_section(
            "Manager Overlap / Duplication Findings",
            _html_table(["Security", "Ticker", "Managers", "Market Value", "Portfolio %"], context["overlap_rows"])
            if context["overlap_rows"]
            else "<p>No direct security overlaps were detected.</p>",
        ),
        _html_section(
            "Scenario Shock Summary",
            "<p>Scenario shocks are deterministic demo approximations, not forecasts.</p>"
            + _html_table(["Scenario", "Before", "After", "Impact", "Impact %"], context["scenario_rows"])
            + f"<p><strong>Primary scenario detail: {escape(primary['scenario_name'])}</strong></p>"
            + f"<p>{escape(primary['description'])}</p>"
            + _html_table(["Holding", "Ticker", "Matched Rule", "Before", "Impact"], context["scenario_impact_rows"]),
        ),
        _html_section(
            "Advisor Talking Points",
            _html_list(context["workflow_talking_points"]),
        ),
        _html_section(
            "Suggested Follow-Up Actions",
            _html_list(context["workflow_follow_up_actions"]),
        ),
        _html_section(
            "Workflow Caveats",
            _html_list(context["workflow_caveats"]),
        ),
        _html_section(
            "What This Demo Proves",
            _html_list(
                [
                    "Arangur v2 can run a complete local portfolio-analysis loop from synthetic fixtures.",
                    "The canonical snapshot can feed valuation, exposure, overlap, scenario, and report generation without source-specific coupling.",
                    "The report can explain holdings, overlap, and scenario impact in advisor-readable language.",
                ]
            ),
        ),
        _html_section(
            "What This Demo Does Not Yet Prove",
            _html_list(
                [
                    "It does not prove live ingestion, Plaid integration, custodian reconciliation, market-data vendor integration, or production data quality.",
                    "It does not implement tax lots, FX, shorts, derivatives, fees, corporate actions, performance attribution, or advanced accounting.",
                    "It does not use or validate legacy MATLAB logic.",
                ]
            ),
        ),
        _html_section(
            "Next Planned Upgrades",
            _html_list(
                [
                    context["workflow_next_upgrade_path"],
                    "Add stronger validation edge cases and report-quality tests around malformed local fixtures.",
                    "Design the future Plaid Sandbox boundary without committing credentials or using real client data.",
                ]
            ),
        ),
    ]
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "  <meta charset=\"utf-8\">",
            f"  <title>{escape(context['title'])}</title>",
            "  <style>",
            "    body { font-family: Arial, sans-serif; line-height: 1.45; margin: 32px; color: #1f2933; }",
            "    h1, h2, h3 { color: #102a43; }",
            "    table { border-collapse: collapse; width: 100%; margin: 12px 0 24px; }",
            "    th, td { border: 1px solid #d9e2ec; padding: 8px 10px; text-align: left; }",
            "    th { background: #f0f4f8; }",
            "    .caveat { background: #fff7ed; border-left: 4px solid #f97316; padding: 12px; }",
            "  </style>",
            "</head>",
            "<body>",
            f"<h1>{escape(context['title'])}</h1>",
            *sections,
            "</body>",
            "</html>",
        ]
    )


def _data_coverage_context(
    data_coverage_result: dict[str, Any] | None,
    workflow: dict[str, Any],
) -> dict[str, Any]:
    if not data_coverage_result:
        return {
            "available": False,
            "detailed": False,
            "summary_lines": ["No data coverage result was supplied for this report run."],
            "dimension_rows": [],
            "key_flags": ["No data coverage flags are available."],
            "human_review_lines": ["No data coverage human-review list is available."],
            "caveats": [],
            "next_items": [],
        }

    portfolio_summary = data_coverage_result["portfolio_coverage_summary"]
    confidence = data_coverage_result["valuation_confidence_summary"]
    human_count = portfolio_summary["human_review_item_count"]
    flags = data_coverage_result["data_quality_flags"]
    human_review_items = data_coverage_result["human_review_items"]
    dimension_rows = [
        [_dimension_label(dimension), _confidence_label(value)]
        for dimension, value in confidence["dimension_confidence"].items()
    ]
    key_flags = [flag["message"] for flag in flags[:5]]
    if not key_flags:
        key_flags = ["No high-priority data quality flags were produced by the current prototype rules."]
    human_review_lines = [item["message"] for item in human_review_items[:6]]
    if not human_review_lines:
        human_review_lines = ["No human-review items were produced by the current prototype rules."]
    return {
        "available": True,
        "detailed": workflow["workflow_type"] == "data_coverage_review",
        "summary_lines": [
            f"Valuation confidence: {_confidence_label(confidence['overall_confidence'])}. {portfolio_summary['summary']}",
            f"Human review items: {human_count}.",
            "Data coverage result: data_coverage_result.json.",
        ],
        "dimension_rows": dimension_rows,
        "key_flags": key_flags,
        "human_review_lines": human_review_lines,
        "caveats": data_coverage_result["caveats"],
        "next_items": data_coverage_result["next_data_work_items"],
    }


def _markdown_data_coverage_section(data_coverage: dict[str, Any]) -> list[str]:
    lines = [
        "## Data Coverage and Valuation Confidence",
        "",
        *_bullets(data_coverage["summary_lines"]),
    ]
    if data_coverage["detailed"]:
        lines.extend(
            [
                "",
                "### Confidence Dimensions",
                "",
                _markdown_table(["Dimension", "Confidence"], data_coverage["dimension_rows"]),
                "",
                "### Key Data Quality Flags",
                "",
                *_bullets(data_coverage["key_flags"]),
                "",
                "### Human Review Items",
                "",
                *_bullets(data_coverage["human_review_lines"]),
                "",
                "### Coverage Caveats",
                "",
                *_bullets(data_coverage["caveats"]),
                "",
                "### Next Data Work Items",
                "",
                *_bullets(data_coverage["next_items"]),
            ]
        )
    else:
        lines.extend(
            [
                "",
                "### Key Data Quality Flags",
                "",
                *_bullets(data_coverage["key_flags"][:3]),
            ]
        )
    return lines


def _html_data_coverage_section(data_coverage: dict[str, Any]) -> str:
    body = _html_list(data_coverage["summary_lines"])
    if data_coverage["detailed"]:
        body += "<h3>Confidence Dimensions</h3>"
        body += _html_table(["Dimension", "Confidence"], data_coverage["dimension_rows"])
        body += "<h3>Key Data Quality Flags</h3>"
        body += _html_list(data_coverage["key_flags"])
        body += "<h3>Human Review Items</h3>"
        body += _html_list(data_coverage["human_review_lines"])
        body += "<h3>Coverage Caveats</h3>"
        body += _html_list(data_coverage["caveats"])
        body += "<h3>Next Data Work Items</h3>"
        body += _html_list(data_coverage["next_items"])
    else:
        body += "<h3>Key Data Quality Flags</h3>"
        body += _html_list(data_coverage["key_flags"][:3])
    return _html_section("Data Coverage and Valuation Confidence", body)


def _dimension_label(value: str) -> str:
    return value.replace("_", " ").title()


def _confidence_label(value: str) -> str:
    return value.replace("_", " ").title()


def _exposure_rows(rows: list[dict[str, Any]]) -> list[list[str]]:
    return [[row["bucket_label"], _currency(row["market_value"]), _percent_value(row["portfolio_percent"])] for row in rows]


def _overlap_rows(overlaps: list[dict[str, Any]]) -> list[list[str]]:
    return [
        [
            row["display_name"],
            row.get("ticker") or "",
            ", ".join(row["manager_names"]),
            _currency(row["total_market_value"]),
            _percent_value(row["portfolio_percent"]),
        ]
        for row in overlaps
    ]


def _overlap_summary(largest_overlap: dict[str, Any] | None) -> str:
    if not largest_overlap:
        return "No direct security overlap was detected in this synthetic dataset."
    return (
        f"The largest direct overlap is {largest_overlap['display_name']} across "
        f"{', '.join(largest_overlap['manager_names'])}, totaling {_currency(largest_overlap['total_market_value'])}."
    )


def _markdown_overlap_section(rows: list[list[str]]) -> str:
    if not rows:
        return "No direct security overlaps were detected."
    return _markdown_table(["Security", "Ticker", "Managers", "Market Value", "Portfolio %"], rows)


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def _html_section(title: str, body: str) -> str:
    return f"<section><h2>{escape(title)}</h2>{body}</section>"


def _html_table(headers: list[str], rows: list[list[str]]) -> str:
    header_html = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    row_html = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(cell))}</td>" for cell in row)
        row_html.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{''.join(row_html)}</tbody></table>"


def _html_list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def _default_workflow_template() -> dict[str, Any]:
    return {
        "workflow_type": "general_review",
        "display_name": "General Review",
        "intended_audience": "Advisor colleague reviewing the local demo.",
        "meeting_goal": "Review the synthetic portfolio analysis in a general advisor-readable format.",
        "primary_questions": [
            "What does the local demo show?",
            "Which exposures, overlaps, and scenarios are visible?",
        ],
        "emphasized_report_sections": [
            "Executive Summary",
            "Portfolio Value Summary",
            "Scenario Shock Summary",
        ],
        "de_emphasized_sections": [],
        "required_inputs": [
            "CanonicalPortfolioSnapshot",
            "ValuationResult",
            "ExposureOverlapResult",
            "ScenarioResult",
        ],
        "advisor_talking_points": [
            "The consolidated view surfaces manager-level concentration and overlap that would be easy to miss account by account.",
            "Microsoft and NVIDIA are deliberately duplicated across managers, giving the advisor a concrete overlap discussion.",
            "The AI/chips scenario links theme exposure to a simple downside story while preserving clear caveats.",
            "Cash and fixed income soften the scenario impact but do not erase concentration in growth-oriented holdings.",
        ],
        "caveats": [
            "This is a synthetic local demo and is not investment advice.",
            "Scenario shocks are deterministic assumptions, not forecasts.",
        ],
        "suggested_follow_up_actions": [
            "Review whether the workflow should be specialized before a colleague walkthrough.",
        ],
        "next_upgrade_path": "Select a workflow-specific template for advisor meeting preparation.",
    }


def _bullets(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def _stable_output_path(output_path: Path) -> str:
    parts = output_path.parts
    if "reports" in parts:
        start = parts.index("reports")
        return "/".join(parts[start:])
    return output_path.name


def _currency(value: float) -> str:
    if value < 0:
        return f"-${abs(value):,.2f}"
    return f"${value:,.2f}"


def _percent(value: float, total: float) -> str:
    return _percent_value(_ratio(value, total))


def _ratio(value: float, total: float) -> float:
    if not total:
        return 0.0
    return float(value) / total


def _percent_value(value: float) -> str:
    return f"{value * 100:.1f}%"
