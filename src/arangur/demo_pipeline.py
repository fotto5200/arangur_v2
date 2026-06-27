"""Run the full local Arangur v2 demo pipeline."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arangur.canonical_snapshot import build_canonical_snapshot
from arangur.demo_data_loader import load_demo_inputs, load_market_data_fixture, load_scenario_definitions
from arangur.exposure_overlap import calculate_exposure_overlap
from arangur.plaid_mock_adapter import build_canonical_snapshot_from_plaid_mock, load_plaid_mock_fixture
from arangur.report_index import build_report_index
from arangur.report_generator import generate_markdown_report
from arangur.scenarios import calculate_scenario_results
from arangur.valuation import calculate_valuation
from arangur.workflow_templates import (
    SUPPORTED_WORKFLOW_TYPES,
    WorkflowTemplateError,
    get_workflow_template,
)

SOURCE_NAMES = {
    "demo_json": "native_demo",
    "plaid_mock": "plaid_mock",
}


class PipelineError(RuntimeError):
    """Raised when the local demo pipeline cannot complete."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_pipeline(
    root: Path | None = None,
    source: str = "demo_json",
    workflow_type: str = "quarterly_review",
    refresh_index: bool = True,
) -> dict[str, Path]:
    root = root or project_root()
    data_dir = root / "data" / "demo"
    _ensure_supported_source(source)
    workflow_template = get_workflow_template(workflow_type)
    output_dir = _output_dir(root, source, workflow_type)
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot, market_data, scenario_definitions = _load_snapshot_and_common_inputs(data_dir, source)
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
    report_package = generate_markdown_report(
        snapshot,
        valuation,
        exposure_overlap,
        scenario_results,
        report_path,
        workflow_template=workflow_template,
    )
    html_report_path = report_path.with_suffix(".html")
    report_package_path = output_dir / "report_package.json"
    output_paths = {
        "canonical_snapshot": snapshot_path,
        "valuation_result": valuation_path,
        "exposure_overlap_result": exposure_path,
        "scenario_result": scenario_path,
        "report_package": report_package_path,
        "markdown_report": report_path,
        "html_report": html_report_path,
    }
    run_metadata = _build_run_metadata(snapshot, source, workflow_template, output_dir, output_paths)
    report_package["run_id"] = run_metadata["run_id"]
    report_package["workflow_type"] = workflow_type
    report_package["source_name"] = run_metadata["source_name"]
    report_package["source_adapter"] = run_metadata["source_adapter"]
    report_package["workflow_template"] = _package_workflow_template(workflow_template)
    report_package["run_metadata"] = run_metadata
    _write_json(report_package_path, report_package)

    if refresh_index:
        output_paths["report_index"] = build_report_index(root / "reports" / "demo")
    return output_paths


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Run the local Arangur v2 demo pipeline.")
    parser.add_argument(
        "--source",
        choices=["demo_json", "plaid_mock"],
        default="demo_json",
        help="Input adapter to run. Default: demo_json.",
    )
    parser.add_argument(
        "--workflow",
        dest="workflow_type",
        default=None,
        help=(
            "Advisor workflow template to render. "
            f"Supported: {', '.join(SUPPORTED_WORKFLOW_TYPES)}. Default: quarterly_review."
        ),
    )
    parser.add_argument(
        "--workflow-type",
        dest="workflow_type",
        default=None,
        help="Deprecated alias for --workflow.",
    )
    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Refresh reports/demo/index.html from existing report packages without rerunning the pipeline.",
    )
    args = parser.parse_args(argv)

    if args.build_index:
        index_path = build_report_index(project_root() / "reports" / "demo")
        print("Generated Arangur v2 demo report index:")
        print(f"- report_index: {index_path}")
        return 0

    workflow_type = args.workflow_type or "quarterly_review"
    try:
        outputs = run_pipeline(source=args.source, workflow_type=workflow_type)
    except (PipelineError, WorkflowTemplateError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("Generated Arangur v2 demo outputs:")
    for name, path in outputs.items():
        print(f"- {name}: {path}")
    return 0


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_run_metadata(
    snapshot: dict[str, Any],
    source: str,
    workflow_template: dict[str, Any],
    output_dir: Path,
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    source_name = SOURCE_NAMES[source]
    source_adapter = snapshot["source"].get("source_adapter") or snapshot["source"].get("adapter") or source
    generated_at = snapshot.get("created_at") or snapshot["source"].get("imported_at") or snapshot["as_of_date"]
    valuation_date = snapshot["as_of_date"]
    workflow_type = workflow_template["workflow_type"]
    run_id = f"run_{source_name}_{workflow_type}_{valuation_date.replace('-', '_')}"
    return {
        "run_id": run_id,
        "source_name": source_name,
        "source_adapter": source_adapter,
        "generated_at": generated_at,
        "valuation_date": valuation_date,
        "workflow_type": workflow_type,
        "workflow_display_name": workflow_template["display_name"],
        "workflow_label": workflow_template["display_name"],
        "workflow_options": list(SUPPORTED_WORKFLOW_TYPES),
        "workflow_template": _package_workflow_template(workflow_template),
        "output_directory": _stable_output_path(output_dir),
        "report_links": {
            "markdown": _stable_output_path(output_paths["markdown_report"]),
            "html": _stable_output_path(output_paths["html_report"]),
        },
        "json_outputs": {
            "canonical_snapshot": _stable_output_path(output_paths["canonical_snapshot"]),
            "valuation_result": _stable_output_path(output_paths["valuation_result"]),
            "exposure_overlap_result": _stable_output_path(output_paths["exposure_overlap_result"]),
            "scenario_result": _stable_output_path(output_paths["scenario_result"]),
            "report_package": _stable_output_path(output_paths["report_package"]),
        },
        "synthetic_data": bool(snapshot["portfolio"]["is_synthetic"]),
    }


def _package_workflow_template(workflow_template: dict[str, Any]) -> dict[str, Any]:
    return {
        key: workflow_template[key]
        for key in (
            "workflow_type",
            "display_name",
            "intended_audience",
            "meeting_goal",
            "primary_questions",
            "emphasized_report_sections",
            "de_emphasized_sections",
            "required_inputs",
            "advisor_talking_points",
            "caveats",
            "suggested_follow_up_actions",
            "next_upgrade_path",
        )
    }


def _load_snapshot_and_common_inputs(data_dir: Path, source: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    market_data = load_market_data_fixture(data_dir)
    scenario_definitions = load_scenario_definitions(data_dir)
    if source == "demo_json":
        portfolio_data, _, _ = load_demo_inputs(data_dir)
        snapshot = build_canonical_snapshot(
            portfolio_data,
            source_files=[
                "data/demo/demo_portfolio.json",
                "data/demo/market_data_fixture.json",
                "data/demo/scenario_definitions.json",
            ],
        )
        return snapshot, market_data, scenario_definitions
    if source == "plaid_mock":
        plaid_data = load_plaid_mock_fixture(data_dir)
        snapshot = build_canonical_snapshot_from_plaid_mock(
            plaid_data,
            source_files=[
                "data/demo/plaid_mock_investments.json",
                "data/demo/market_data_fixture.json",
                "data/demo/scenario_definitions.json",
            ],
        )
        return snapshot, market_data, scenario_definitions
    raise PipelineError(f"Unsupported source adapter: {source}")


def _output_dir(root: Path, source: str, workflow_type: str) -> Path:
    base = root / "reports" / "demo"
    if source == "demo_json":
        if workflow_type == "quarterly_review":
            return base
        return base / "workflows" / workflow_type
    if source == "plaid_mock":
        source_base = base / "plaid_mock"
        if workflow_type == "quarterly_review":
            return source_base
        return source_base / "workflows" / workflow_type
    raise PipelineError(f"Unsupported source adapter: {source}")


def _ensure_supported_source(source: str) -> None:
    if source not in SOURCE_NAMES:
        raise PipelineError(f"Unsupported source adapter: {source}")


def _ensure_valid(validation: dict[str, Any], stage: str) -> None:
    if validation.get("status") == "valid":
        return
    messages = [f"{stage} validation failed:"]
    for error in validation.get("errors", []):
        messages.append(f"- {error.get('code')}: {error.get('record_id')} - {error.get('message')}")
    raise PipelineError("\n".join(messages))


def _stable_output_path(path: Path) -> str:
    parts = path.parts
    if "reports" in parts:
        start = parts.index("reports")
        return "/".join(parts[start:])
    return path.name


if __name__ == "__main__":
    raise SystemExit(main())
