"""Generate a static local index for demo report outputs."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


INDEX_TITLE = "Arangur Demo Report Index"
SYNTHETIC_DATA_CAVEAT = (
    "Demo only: these report runs use synthetic local data. They are not client statements, "
    "investment advice, production valuations, or evidence of live Plaid integration."
)

JSON_OUTPUT_FILES = [
    ("Canonical snapshot JSON", "canonical_portfolio_snapshot.json"),
    ("Valuation result JSON", "valuation_result.json"),
    ("Exposure overlap result JSON", "exposure_overlap_result.json"),
    ("Scenario result JSON", "scenario_result.json"),
    ("Report package JSON", "report_package.json"),
]


def build_report_index(reports_dir: Path) -> Path:
    """Build reports/demo/index.html from available report_package.json files."""

    reports_dir.mkdir(parents=True, exist_ok=True)
    runs = collect_report_runs(reports_dir)
    index_path = reports_dir / "index.html"
    index_path.write_text(render_report_index_html(runs), encoding="utf-8")
    return index_path


def collect_report_runs(reports_dir: Path) -> list[dict[str, Any]]:
    """Collect report run records by scanning for report_package.json files."""

    runs: list[dict[str, Any]] = []
    for package_path in sorted(reports_dir.rglob("report_package.json")):
        package = _load_json(package_path)
        runs.append(_run_from_package(reports_dir, package_path, package))
    return sorted(runs, key=_run_sort_key)


def render_report_index_html(runs: list[dict[str, Any]]) -> str:
    run_sections = [_render_run_section(run) for run in runs]
    if not run_sections:
        run_sections = ["<p>No report packages were found under this demo reports directory.</p>"]

    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "  <meta charset=\"utf-8\">",
            f"  <title>{escape(INDEX_TITLE)}</title>",
            "  <style>",
            "    body { font-family: Arial, sans-serif; line-height: 1.45; margin: 32px; color: #1f2933; }",
            "    h1, h2, h3 { color: #102a43; }",
            "    a { color: #0b63ce; }",
            "    section { border-top: 1px solid #d9e2ec; padding-top: 20px; margin-top: 24px; }",
            "    .caveat { background: #fff7ed; border-left: 4px solid #f97316; padding: 12px; }",
            "    .run-meta { display: grid; grid-template-columns: max-content 1fr; gap: 6px 14px; }",
            "    .run-meta dt { font-weight: bold; }",
            "    ul { padding-left: 22px; }",
            "  </style>",
            "</head>",
            "<body>",
            f"<h1>{escape(INDEX_TITLE)}</h1>",
            f"<p class=\"caveat\">{escape(SYNTHETIC_DATA_CAVEAT)}</p>",
            "<section>",
            "<h2>What This Demo Proves</h2>",
            "<ul>",
            "<li>Arangur v2 can generate advisor-readable reports from local synthetic fixtures.</li>",
            "<li>The same analytics and report components can run from multiple source adapters.</li>",
            "<li>Report packages now carry simple workflow-run metadata for local browsing.</li>",
            "</ul>",
            "</section>",
            "<section>",
            "<h2>What This Demo Does Not Yet Prove</h2>",
            "<ul>",
            "<li>It does not prove live Plaid ingestion, external market data, or production reconciliation.</li>",
            "<li>It does not use real client data, credentials, or legacy MATLAB outputs.</li>",
            "<li>It does not implement a production dashboard or advisor assistant workflow.</li>",
            "</ul>",
            "</section>",
            "<section>",
            "<h2>Available Report Runs</h2>",
            *run_sections,
            "</section>",
            "</body>",
            "</html>",
        ]
    )


def _run_from_package(reports_dir: Path, package_path: Path, package: dict[str, Any]) -> dict[str, Any]:
    package_dir = package_path.parent
    metadata = package.get("run_metadata", {})
    workflow_template = package.get("workflow_template") or metadata.get("workflow_template") or {}
    source_name = metadata.get("source_name") or package.get("source_name") or "unknown_source"
    workflow_type = metadata.get("workflow_type") or package.get("workflow_type") or "unknown_workflow"
    return {
        "run_id": metadata.get("run_id") or package.get("run_id") or package["report_id"],
        "source_name": source_name,
        "source_adapter": metadata.get("source_adapter") or package.get("source_adapter") or source_name,
        "workflow_type": workflow_type,
        "workflow_label": metadata.get("workflow_display_name") or metadata.get("workflow_label") or workflow_template.get("display_name") or _label(workflow_type),
        "meeting_goal": workflow_template.get("meeting_goal") or metadata.get("meeting_goal") or "",
        "generated_at": metadata.get("generated_at") or "",
        "valuation_date": metadata.get("valuation_date") or package.get("valuation_date") or "",
        "synthetic_data": metadata.get("synthetic_data", package.get("is_synthetic")),
        "output_directory": metadata.get("output_directory") or _relative_display(reports_dir, package_dir),
        "report_title": package.get("report_title", "Untitled Report"),
        "report_links": _report_links(reports_dir, package_dir, package),
        "json_links": _json_links(reports_dir, package_dir),
    }


def _render_run_section(run: dict[str, Any]) -> str:
    report_links = _link_list(run["report_links"])
    json_links = _link_list(run["json_links"])
    return "\n".join(
        [
            "<section>",
            f"<h3>{escape(run['report_title'])}</h3>",
            "<dl class=\"run-meta\">",
            f"<dt>Run ID</dt><dd>{escape(run['run_id'])}</dd>",
            f"<dt>Source</dt><dd>{escape(run['source_name'])}</dd>",
            f"<dt>Source adapter</dt><dd>{escape(run['source_adapter'])}</dd>",
            f"<dt>Workflow</dt><dd>{escape(run['workflow_label'])} ({escape(run['workflow_type'])})</dd>",
            f"<dt>Meeting goal</dt><dd>{escape(run['meeting_goal'])}</dd>",
            f"<dt>Valuation date</dt><dd>{escape(run['valuation_date'])}</dd>",
            f"<dt>Generated at</dt><dd>{escape(run['generated_at'])}</dd>",
            f"<dt>Output directory</dt><dd>{escape(run['output_directory'])}</dd>",
            f"<dt>Synthetic data</dt><dd>{escape(str(run['synthetic_data']))}</dd>",
            "</dl>",
            "<h4>Reports</h4>",
            report_links,
            "<h4>JSON Outputs</h4>",
            json_links,
            "</section>",
        ]
    )


def _report_links(reports_dir: Path, package_dir: Path, package: dict[str, Any]) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for output in package.get("outputs", []):
        output_format = output.get("format")
        output_path = _resolve_stable_output_path(reports_dir, package_dir, output.get("path", ""))
        if output_path.exists():
            links.append(
                {
                    "label": f"{_label(str(output_format))} report",
                    "href": _href(reports_dir, output_path),
                }
            )
    return links


def _json_links(reports_dir: Path, package_dir: Path) -> list[dict[str, str]]:
    links = []
    for label, filename in JSON_OUTPUT_FILES:
        path = package_dir / filename
        if path.exists():
            links.append({"label": label, "href": _href(reports_dir, path)})
    return links


def _link_list(links: list[dict[str, str]]) -> str:
    if not links:
        return "<p>No linked outputs were found.</p>"
    items = [
        f"<li><a href=\"{escape(link['href'], quote=True)}\">{escape(link['label'])}</a></li>"
        for link in links
    ]
    return "<ul>" + "".join(items) + "</ul>"


def _resolve_stable_output_path(reports_dir: Path, package_dir: Path, stable_path: str) -> Path:
    parts = str(stable_path).replace("\\", "/").split("/")
    if len(parts) >= 2 and parts[0] == "reports" and parts[1] == "demo":
        return reports_dir.joinpath(*parts[2:])
    return package_dir / Path(stable_path).name


def _href(reports_dir: Path, path: Path) -> str:
    return path.relative_to(reports_dir).as_posix()


def _relative_display(reports_dir: Path, path: Path) -> str:
    relative = path.relative_to(reports_dir).as_posix()
    return "reports/demo" if relative == "." else f"reports/demo/{relative}"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def _run_sort_key(run: dict[str, Any]) -> tuple[int, str, str]:
    native_rank = 0 if run["source_name"] == "native_demo" else 1
    return (native_rank, run["source_name"], run["run_id"])


def _label(value: str) -> str:
    if value.lower() == "html":
        return "HTML"
    return value.replace("_", " ").title()
