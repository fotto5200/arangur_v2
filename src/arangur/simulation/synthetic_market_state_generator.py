"""CLI for writing deterministic synthetic market-state fixtures."""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arangur.simulation.market_state import (
    DEFAULT_HISTORY_OUTPUT_PATH,
    DEFAULT_SCENARIO_OUTPUT_PATH,
    DEFAULT_SEED,
    DEFAULT_SUMMARY_OUTPUT_PATH,
    build_synthetic_market_state_summary,
    validate_synthetic_market_state_history,
    write_synthetic_market_state_history,
)
from arangur.simulation.position_universe import DEFAULT_OUTPUT_PATH as DEFAULT_POSITION_UNIVERSE_PATH
from arangur.simulation.position_universe import load_synthetic_position_universe


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Generate Arangur synthetic market-state fixtures.")
    parser.add_argument(
        "--position-universe",
        default=str(DEFAULT_POSITION_UNIVERSE_PATH),
        help=f"Position universe input path. Default: {DEFAULT_POSITION_UNIVERSE_PATH}",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_HISTORY_OUTPUT_PATH),
        help=f"Market-state history output path. Default: {DEFAULT_HISTORY_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--summary-output",
        default=str(DEFAULT_SUMMARY_OUTPUT_PATH),
        help=f"Summary output path. Default: {DEFAULT_SUMMARY_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--scenario-output",
        default=str(DEFAULT_SCENARIO_OUTPUT_PATH),
        help=f"Scenario output path. Default: {DEFAULT_SCENARIO_OUTPUT_PATH}",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"Deterministic seed. Default: {DEFAULT_SEED}")
    args = parser.parse_args(argv)

    history = write_synthetic_market_state_history(
        args.output,
        position_universe_path=args.position_universe,
        seed=args.seed,
        summary_path=args.summary_output,
        scenario_path=args.scenario_output,
    )
    position_universe = load_synthetic_position_universe(args.position_universe)
    validation = validate_synthetic_market_state_history(history, position_universe)
    if validation["status"] != "valid":
        print("Synthetic market-state validation failed:", file=sys.stderr)
        for error in validation["errors"]:
            print(f"- {error['code']}: {error['record_id']} - {error['message']}", file=sys.stderr)
        return 1

    summary = build_synthetic_market_state_summary(history, position_universe)
    print("Generated Arangur synthetic market state:")
    print(f"- output: {Path(args.output)}")
    print(f"- summary_output: {Path(args.summary_output)}")
    print(f"- scenario_output: {Path(args.scenario_output)}")
    print(f"- dates_generated: {summary['date_count']}")
    print(f"- core_drivers: {summary['core_driver_count']}")
    print(f"- expanded_variables: {summary['expanded_state_variable_count']}")
    print(f"- scenarios: {summary['scenario_count']}")
    print(f"- required_variables_covered: {len(summary['required_state_variables_covered'])}")
    print(f"- human_review_items: {summary['human_review_state_count']}")
    print(f"- covariance_recovery_status: {summary['covariance_recovery_summary']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
