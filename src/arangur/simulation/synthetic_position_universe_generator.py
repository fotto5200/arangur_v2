"""CLI for writing the deterministic synthetic position universe fixture."""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arangur.simulation.position_universe import (
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SEED,
    DEFAULT_SUMMARY_OUTPUT_PATH,
    build_synthetic_position_universe_summary,
    validate_synthetic_position_universe,
    write_synthetic_position_universe,
)


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Generate the Arangur synthetic position universe fixture.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Main JSON output path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    parser.add_argument(
        "--summary-output",
        default=str(DEFAULT_SUMMARY_OUTPUT_PATH),
        help=f"Summary JSON output path. Default: {DEFAULT_SUMMARY_OUTPUT_PATH}",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"Deterministic seed. Default: {DEFAULT_SEED}")
    args = parser.parse_args(argv)

    universe = write_synthetic_position_universe(args.output, seed=args.seed, summary_path=args.summary_output)
    validation = validate_synthetic_position_universe(universe)
    if validation["status"] != "valid":
        print("Synthetic position universe validation failed:", file=sys.stderr)
        for error in validation["errors"]:
            print(f"- {error['code']}: {error['record_id']} - {error['message']}", file=sys.stderr)
        return 1

    summary = build_synthetic_position_universe_summary(universe)
    print("Generated Arangur synthetic position universe:")
    print(f"- output: {Path(args.output)}")
    print(f"- summary_output: {Path(args.summary_output)}")
    print(f"- managers: {summary['manager_count']}")
    print(f"- accounts: {summary['account_count']}")
    print(f"- sleeves: {summary['sleeve_count']}")
    print(f"- positions: {summary['position_count']}")
    print(f"- transactions: {summary['transaction_count']}")
    print(f"- asset_classes: {', '.join(summary['asset_classes'])}")
    print(f"- themes: {', '.join(summary['themes'])}")
    print(f"- human_review_count: {summary['human_review_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
