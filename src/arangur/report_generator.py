"""Generate the advisor-readable Markdown report for the local demo."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_markdown_report(
    snapshot: dict[str, Any],
    valuation: dict[str, Any],
    exposure_overlap: dict[str, Any],
    scenario_result_set: dict[str, Any],
    output_path: Path,
) -> dict[str, Any]:
    scenario_results = scenario_result_set["scenario_results"]
    primary_scenario = scenario_results[0]
    markdown = "\n".join(
        [
            f"# {snapshot['portfolio']['portfolio_name']} Review",
            "",
            "**Demo only:** this report uses synthetic data and local fixture prices. It is intended to demonstrate Arangur v2 product behavior and is not investment advice, a client statement, or a production valuation.",
            "",
            "## Portfolio Summary",
            "",
            f"- Portfolio: {snapshot['portfolio']['owner_label']}",
            f"- Advisor label: {snapshot['portfolio'].get('advisor_label') or 'N/A'}",
            f"- Valuation date: {snapshot['as_of_date']}",
            f"- Total value: {_currency(valuation['portfolio_total']['market_value'])}",
            f"- Cash: {_currency(valuation['portfolio_total']['cash_value'])} ({_percent(valuation['portfolio_total']['cash_value'], valuation['portfolio_total']['market_value'])})",
            "",
            "## Manager Summary",
            "",
            _table(
                ["Manager", "Market Value", "Portfolio %"],
                [
                    [row["manager_name"], _currency(row["market_value"]), _percent(row["market_value"], valuation["portfolio_total"]["market_value"])]
                    for row in valuation["manager_totals"]
                ],
            ),
            "",
            "## Account Summary",
            "",
            _table(
                ["Account", "Manager", "Market Value", "Cash"],
                [
                    [row["account_name"], row["manager_name"], _currency(row["market_value"]), _currency(row["cash_value"])]
                    for row in valuation["account_totals"]
                ],
            ),
            "",
            "## Top Holdings",
            "",
            _table(
                ["Holding", "Ticker", "Manager", "Market Value", "Portfolio %"],
                [
                    [
                        row["display_name"],
                        row.get("ticker") or "",
                        row["manager_name"],
                        _currency(row["market_value"]),
                        _percent(row["market_value"], valuation["portfolio_total"]["market_value"]),
                    ]
                    for row in exposure_overlap["top_holdings"][:8]
                ],
            ),
            "",
            "## Sector Exposure",
            "",
            _exposure_table(exposure_overlap["exposures"]["by_sector"][:8]),
            "",
            "## Theme Exposure",
            "",
            "Theme exposure can exceed 100% in aggregate because a security can carry multiple theme tags.",
            "",
            _exposure_table(exposure_overlap["exposures"]["by_theme"][:10]),
            "",
            "## Overlap And Duplication Findings",
            "",
            _overlap_section(exposure_overlap),
            "",
            "## Scenario Shock Summary",
            "",
            f"Primary scenario: **{primary_scenario['scenario_name']}**",
            "",
            primary_scenario["description"],
            "",
            _table(
                ["Before", "After", "Impact", "Impact %"],
                [
                    [
                        _currency(primary_scenario["portfolio_before_value"]),
                        _currency(primary_scenario["portfolio_after_value"]),
                        _currency(primary_scenario["portfolio_impact_value"]),
                        _percent_value(primary_scenario["portfolio_impact_percent"]),
                    ]
                ],
            ),
            "",
            "Largest position impacts:",
            "",
            _table(
                ["Holding", "Ticker", "Rule", "Impact"],
                [
                    [
                        row["display_name"],
                        row.get("ticker") or "",
                        row["matched_rule"],
                        _currency(row["impact_value"]),
                    ]
                    for row in sorted(primary_scenario["position_impacts"], key=lambda item: item["impact_value"])[:8]
                ],
            ),
            "",
            "## Advisor Talking Points",
            "",
            "- The consolidated view shows that AI/chips exposure is larger than any single account suggests.",
            "- Microsoft and NVIDIA appear across multiple managers, making the overlap intentionality worth discussing.",
            "- Cash and fixed income reduce total scenario impact, but the growth sleeve still drives visible downside in the AI/chips shock.",
            "- The first demo is useful for discussing concentration, overlap, and scenario storytelling before adding live ingestion.",
            "",
            "## Limitations And Caveats",
            "",
            "- Data is synthetic and hand-authored for product demonstration.",
            "- Prices, sectors, themes, and scenario rules come from local fixtures.",
            "- Scenario shocks are deterministic approximations, not forecasts.",
            "- The report is not investment advice and should not be treated as a client statement.",
            "- V1 uses long-only holdings, cash at face value, one reporting currency, direct holdings, and simple aggregation.",
            "- Plaid, custodian ingestion, market data vendors, deeper valuation, accounting, and MATLAB-informed upgrades are future adapters or upgrades.",
            "",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    return {
        "schema_version": "report_package.v1",
        "report_id": "arangur_demo_report",
        "report_title": f"{snapshot['portfolio']['portfolio_name']} Review",
        "valuation_date": snapshot["as_of_date"],
        "portfolio_id": snapshot["portfolio"]["portfolio_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "is_synthetic": snapshot["portfolio"]["is_synthetic"],
        "audience": "advisor_colleague_demo",
        "outputs": [{"format": "markdown", "path": _stable_output_path(output_path)}],
    }


def _exposure_table(rows: list[dict[str, Any]]) -> str:
    return _table(
        ["Bucket", "Market Value", "Portfolio %"],
        [[row["bucket_label"], _currency(row["market_value"]), _percent_value(row["portfolio_percent"])] for row in rows],
    )


def _overlap_section(exposure_overlap: dict[str, Any]) -> str:
    overlaps = exposure_overlap["overlaps"]
    if not overlaps:
        return "No direct security overlaps were detected."
    return _table(
        ["Security", "Ticker", "Managers", "Market Value", "Portfolio %"],
        [
            [
                row["display_name"],
                row.get("ticker") or "",
                ", ".join(row["manager_names"]),
                _currency(row["total_market_value"]),
                _percent_value(row["portfolio_percent"]),
            ]
            for row in overlaps[:8]
        ],
    )


def _table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def _stable_output_path(output_path: Path) -> str:
    parts = output_path.parts
    if "reports" in parts:
        start = parts.index("reports")
        return "/".join(parts[start:])
    return output_path.name


def _currency(value: float) -> str:
    return f"${value:,.2f}"


def _percent(value: float, total: float) -> str:
    if not total:
        return "0.0%"
    return _percent_value(value / total)


def _percent_value(value: float) -> str:
    return f"{value * 100:.1f}%"
