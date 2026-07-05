from __future__ import annotations

import argparse
from pathlib import Path

from arangur.analytics.revaluation import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_POSITION_UNIVERSE_PATH,
    DEFAULT_SCENARIO_MARKET_STATES_PATH,
    run_full_revaluation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the synthetic internal full-revaluation fixture bundle.",
    )
    parser.add_argument(
        "--position-universe",
        default=str(DEFAULT_POSITION_UNIVERSE_PATH),
        help="Synthetic position universe fixture path.",
    )
    parser.add_argument(
        "--scenario-market-states",
        default=str(DEFAULT_SCENARIO_MARKET_STATES_PATH),
        help="Synthetic scenario market-state fixture path.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for generated revaluation fixtures and outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    outputs = run_full_revaluation(
        position_universe_path=Path(args.position_universe),
        scenario_market_states_path=Path(args.scenario_market_states),
        output_dir=Path(args.output_dir),
    )
    manifest = outputs["revaluation_bundle_manifest"]
    coverage = manifest["coverage_summary"]["by_status"]

    print("Synthetic full revaluation bundle generated")
    print(f"Output directory: {Path(args.output_dir)}")
    print(f"Scenario: {manifest['scenario_id']}")
    print(f"Positions: {manifest['position_count']}")
    print(f"Base portfolio value: {manifest['base_portfolio_value']}")
    print(f"Scenario portfolio value: {manifest['scenario_portfolio_value']}")
    print(f"Impact: {manifest['impact']} ({manifest['impact_percent']})")
    print(
        "Coverage: "
        + ", ".join(f"{status}={row['count']}" for status, row in sorted(coverage.items()))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
