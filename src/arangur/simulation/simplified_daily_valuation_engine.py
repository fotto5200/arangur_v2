"""CLI for writing deterministic simplified daily valuation fixtures."""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arangur.simulation.daily_valuation import (
    DEFAULT_DAILY_PORTFOLIO_OUTPUT_PATH,
    DEFAULT_DAILY_POSITION_OUTPUT_PATH,
    DEFAULT_MARKET_STATE_HISTORY_PATH,
    DEFAULT_POSITION_UNIVERSE_PATH,
    DEFAULT_SCENARIO_MARKET_STATES_PATH,
    DEFAULT_SCENARIO_REVALUATION_OUTPUT_PATH,
    DEFAULT_SUMMARY_OUTPUT_PATH,
    DEFAULT_VALUE_CHANGE_OUTPUT_PATH,
    write_daily_valuation_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Generate Arangur simplified daily valuation fixtures.")
    parser.add_argument(
        "--position-universe",
        default=str(DEFAULT_POSITION_UNIVERSE_PATH),
        help=f"Position universe input path. Default: {DEFAULT_POSITION_UNIVERSE_PATH}",
    )
    parser.add_argument(
        "--market-state-history",
        default=str(DEFAULT_MARKET_STATE_HISTORY_PATH),
        help=f"Market-state history input path. Default: {DEFAULT_MARKET_STATE_HISTORY_PATH}",
    )
    parser.add_argument(
        "--scenario-market-states",
        default=str(DEFAULT_SCENARIO_MARKET_STATES_PATH),
        help=f"Scenario market-state input path. Default: {DEFAULT_SCENARIO_MARKET_STATES_PATH}",
    )
    parser.add_argument(
        "--daily-position-output",
        default=str(DEFAULT_DAILY_POSITION_OUTPUT_PATH),
        help=f"Daily position valuation output path. Default: {DEFAULT_DAILY_POSITION_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--daily-portfolio-output",
        default=str(DEFAULT_DAILY_PORTFOLIO_OUTPUT_PATH),
        help=f"Daily portfolio valuation output path. Default: {DEFAULT_DAILY_PORTFOLIO_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--value-change-output",
        default=str(DEFAULT_VALUE_CHANGE_OUTPUT_PATH),
        help=f"Value-change package output path. Default: {DEFAULT_VALUE_CHANGE_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--scenario-revaluation-output",
        default=str(DEFAULT_SCENARIO_REVALUATION_OUTPUT_PATH),
        help=f"Scenario revaluation output path. Default: {DEFAULT_SCENARIO_REVALUATION_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--summary-output",
        default=str(DEFAULT_SUMMARY_OUTPUT_PATH),
        help=f"Simplified valuation summary output path. Default: {DEFAULT_SUMMARY_OUTPUT_PATH}",
    )
    args = parser.parse_args(argv)

    generated = write_daily_valuation_outputs(
        position_universe_path=args.position_universe,
        market_state_history_path=args.market_state_history,
        scenario_market_states_path=args.scenario_market_states,
        daily_position_output_path=args.daily_position_output,
        daily_portfolio_output_path=args.daily_portfolio_output,
        value_change_output_path=args.value_change_output,
        scenario_revaluation_output_path=args.scenario_revaluation_output,
        summary_output_path=args.summary_output,
    )
    summary = generated["summary"]
    validation = generated["validation"]
    if validation["status"] != "valid":
        print("Simplified valuation validation failed:", file=sys.stderr)
        for error in validation["errors"]:
            print(f"- {error['code']}: {error['record_id']} - {error['message']}", file=sys.stderr)
        return 1

    print("Generated Arangur simplified daily valuation:")
    print(f"- daily_position_output: {Path(args.daily_position_output)}")
    print(f"- daily_portfolio_output: {Path(args.daily_portfolio_output)}")
    print(f"- value_change_output: {Path(args.value_change_output)}")
    print(f"- scenario_revaluation_output: {Path(args.scenario_revaluation_output)}")
    print(f"- summary_output: {Path(args.summary_output)}")
    print(f"- dates_valued: {summary['date_count']}")
    print(f"- positions_valued: {summary['position_count']}")
    print(f"- current_portfolio_value: {summary['total_current_portfolio_value']}")
    print(f"- scenario_count: {summary['scenario_count']}")
    print(f"- human_review_count: {summary['human_review_count']}")
    print(f"- human_review_value: {summary['human_review_value']}")
    print(f"- validation_status: {summary['validation_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
