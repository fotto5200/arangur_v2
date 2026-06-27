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
) -> dict[str, Any]:
    """Generate the demo Markdown report plus a simple HTML companion."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = output_path.with_suffix(".html")
    context = _build_report_context(snapshot, valuation, exposure_overlap, scenario_result_set)

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
) -> dict[str, Any]:
    total_value = valuation["portfolio_total"]["market_value"]
    cash_value = valuation["portfolio_total"]["cash_value"]
    primary_scenario = scenario_result_set["scenario_results"][0]
    top_theme = exposure_overlap["exposures"]["by_theme"][0]
    top_sector = exposure_overlap["exposures"]["by_sector"][0]
    largest_overlap = exposure_overlap["overlaps"][0] if exposure_overlap["overlaps"] else None

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
        *_bullets(
            [
                "The consolidated view surfaces manager-level concentration and overlap that would be easy to miss account by account.",
                "Microsoft and NVIDIA are deliberately duplicated across managers, giving the advisor a concrete overlap discussion.",
                "The AI/chips scenario links theme exposure to a simple downside story while preserving clear caveats.",
                "Cash and fixed income soften the scenario impact but do not erase concentration in growth-oriented holdings.",
            ]
        ),
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
                "Add a Plaid-shaped mock ingestion adapter that emits the same canonical snapshot contract.",
                "Add stronger validation edge cases and report-quality tests around malformed local fixtures.",
                "Consider a lightweight local report index or viewer after the report package stabilizes.",
            ]
        ),
        "",
    ]
    return "\n".join(lines)


def _render_html(context: dict[str, Any]) -> str:
    primary = context["primary_scenario"]
    sections = [
        _html_section("Synthetic-Data Caveat", f"<p class=\"caveat\">{escape(DEMO_CAVEAT)}</p>"),
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
            _html_list(
                [
                    "The consolidated view surfaces manager-level concentration and overlap that would be easy to miss account by account.",
                    "Microsoft and NVIDIA are deliberately duplicated across managers, giving the advisor a concrete overlap discussion.",
                    "The AI/chips scenario links theme exposure to a simple downside story while preserving clear caveats.",
                    "Cash and fixed income soften the scenario impact but do not erase concentration in growth-oriented holdings.",
                ]
            ),
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
                    "Add a Plaid-shaped mock ingestion adapter that emits the same canonical snapshot contract.",
                    "Add stronger validation edge cases and report-quality tests around malformed local fixtures.",
                    "Consider a lightweight local report index or viewer after the report package stabilizes.",
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
