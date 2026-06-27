"""Run the full local Arangur v2 demo pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arangur.canonical_snapshot import build_canonical_snapshot
from arangur.demo_data_loader import load_demo_inputs
from arangur.exposure_overlap import calculate_exposure_overlap
from arangur.report_generator import generate_markdown_report
from arangur.scenarios import calculate_scenario_results
from arangur.valuation import calculate_valuation


class PipelineError(RuntimeError):
    """Raised when the local demo pipeline cannot complete."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_pipeline(root: Path | None = None) -> dict[str, Path]:
    root = root or project_root()
    data_dir = root / "data" / "demo"
    output_dir = root / "reports" / "demo"
    output_dir.mkdir(parents=True, exist_ok=True)

    portfolio_data, market_data, scenario_definitions = load_demo_inputs(data_dir)
    snapshot = build_canonical_snapshot(
        portfolio_data,
        source_files=[
            "data/demo/demo_portfolio.json",
            "data/demo/market_data_fixture.json",
            "data/demo/scenario_definitions.json",
        ],
    )
    _ensure_valid(snapshot["validation"], "canonical snapshot")
    snapshot_path = output_dir / "canonical_portfolio_snapshot.json"
    _write_json(snapshot_path, snapshot)

    valuation = calculate_valuation(snapshot, market_data)
    _ensure_valid(valuation["validation"], "valuation")
    valuation_path = output_dir / "valuation_result.json"
    _write_json(valuation_path, valuation)

    exposure_overlap = calculate_exposure_overlap(snapshot, valuation)
    exposure_path = output_dir / "exposure_overlap_result.json"
    _write_json(exposure_path, exposure_overlap)

    scenario_results = calculate_scenario_results(snapshot, valuation, scenario_definitions)
    scenario_path = output_dir / "scenario_result.json"
    _write_json(scenario_path, scenario_results)

    report_path = output_dir / "arangur_demo_report.md"
    report_package = generate_markdown_report(snapshot, valuation, exposure_overlap, scenario_results, report_path)
    report_package_path = output_dir / "report_package.json"
    _write_json(report_package_path, report_package)

    return {
        "canonical_snapshot": snapshot_path,
        "valuation_result": valuation_path,
        "exposure_overlap_result": exposure_path,
        "scenario_result": scenario_path,
        "report_package": report_package_path,
        "markdown_report": report_path,
    }


def main() -> int:
    outputs = run_pipeline()
    print("Generated Arangur v2 demo outputs:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")
    return 0


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ensure_valid(validation: dict[str, Any], stage: str) -> None:
    if validation.get("status") == "valid":
        return
    messages = [f"{stage} validation failed:"]
    for error in validation.get("errors", []):
        messages.append(f"- {error.get('code')}: {error.get('record_id')} - {error.get('message')}")
    raise PipelineError("\n".join(messages))


if __name__ == "__main__":
    raise SystemExit(main())
