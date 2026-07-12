"""Advisor-safe views of the committed demo report-workflow catalog."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from typing import Any

from arangur.analytics.report_workflow_catalog import (
    DEFAULT_WORKFLOW_DIR,
    SUPERSEDED_REPORT_IDS,
    WORKFLOW_FILENAMES,
)
from arangur.demo_pipeline import project_root


WORKFLOW_ORDER = tuple(WORKFLOW_FILENAMES)
ADVISOR_WORKFLOW_COPY = {
    "principal_family_office_briefing_minimal_v1": {
        "display_name": "Principal Briefing",
        "description": "A concise principal conversation about portfolio standing, cash needs, the largest risks, and what the advisor plans to watch or do next.",
    },
    "engaged_client_investment_committee_review_v1": {
        "display_name": "Engaged Client Review",
        "description": "A detailed client or investment-committee review of allocation, policy decisions, managers, lens exposures, and scenario downside.",
    },
    "advisor_manager_oversight_v1": {
        "display_name": "Advisor Oversight",
        "description": "An advisor-oriented review of policy drift, mandate benchmarks, attribution, manager implementation, and coverage confidence.",
    },
    "external_manager_story_translation_v1": {
        "display_name": "External Manager Story Translation",
        "description": "A translation of an outside manager worldview into structured lenses, scenarios, candidate proxies, and report workflows.",
    },
}
EXTERNAL_STORY_CAVEATS = (
    "Translation, not endorsement.",
    "Synthetic and not verified.",
    "Not a recommendation.",
    "Candidate proxies require approval.",
    "Review is required before any production client use.",
)
AVAILABLE_STATUSES = {"accepted", "accepted_with_minor_polish", "available", "setup_note"}
PREVIEW_ROOTS = (
    Path("docs/product/report_mockups"),
    Path("data/simulation/external_story_translation"),
)
HIDDEN_PREVIEW_FIELDS = {
    "schema_version",
    "generated_at",
    "workflow_id",
    "report_id",
    "pack_id",
    "pack_version",
    "source_artifact_path",
    "source_mockup_path",
    "source_view_path",
}


class AdvisorWorkflowError(ValueError):
    """Raised when an advisor workflow or preview cannot be resolved safely."""


def list_advisor_workflows(root: Path | None = None) -> dict[str, Any]:
    """Return exactly four normalized journeys, preserving catalog step order."""

    resolved_root = (root or project_root()).resolve()
    workflow_dir = resolved_root / DEFAULT_WORKFLOW_DIR
    journeys = [
        _load_journey(workflow_id, workflow_dir / WORKFLOW_FILENAMES[workflow_id], resolved_root)
        for workflow_id in WORKFLOW_ORDER
    ]
    return {
        "schema_version": "advisor_report_workflow_catalog.v1",
        "workflow_count": len(journeys),
        "workflows": journeys,
    }


def render_report_preview(workflow_id: str, report_id: str, root: Path | None = None) -> str:
    """Render one allowlisted committed workflow artifact as a clean HTML preview."""

    resolved_root = (root or project_root()).resolve()
    catalog = list_advisor_workflows(resolved_root)
    workflow = next((row for row in catalog["workflows"] if row["workflow_id"] == workflow_id), None)
    if not workflow:
        raise AdvisorWorkflowError("Workflow preview is not available.")
    step = next((row for row in workflow["ordered_steps"] if row["report_id"] == report_id), None)
    if not step or not step.get("preview_url"):
        raise AdvisorWorkflowError("This report is not available for preview.")

    source_path = _source_path_for_step(workflow_id, report_id, resolved_root)
    if source_path.suffix.lower() == ".md":
        body = _markdown_body(source_path.read_text(encoding="utf-8"))
    elif source_path.suffix.lower() == ".json":
        body = _json_body(json.loads(source_path.read_text(encoding="utf-8")))
    else:
        raise AdvisorWorkflowError("This report format is not available for preview.")
    caveats = EXTERNAL_STORY_CAVEATS if workflow_id == "external_manager_story_translation_v1" else (
        "Synthetic demo content. Not production reporting or investment advice.",
    )
    caveat_html = "".join(f"<li>{escape(item)}</li>" for item in caveats)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(step['display_title'])} · Arangur</title>
<style>
body{{background:#f6f8f7;color:#1f2933;font:15px/1.5 Arial,sans-serif;margin:0}}main{{background:#fff;margin:28px auto;max-width:920px;padding:28px;border:1px solid #d8e0df;border-radius:10px}}a{{color:#0f766e}}h1,h2,h3{{color:#102a43}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #d8e0df;padding:8px;text-align:left;vertical-align:top}}.context,.caveats{{color:#62717d}}.caveats{{border-top:1px solid #d8e0df;margin-top:24px;padding-top:16px}}.field{{border-bottom:1px solid #edf1f0;padding:10px 0}}.field strong{{color:#102a43;display:block}}ul{{padding-left:22px}}@media(max-width:640px){{main{{border:0;margin:0;padding:20px}}}}
</style></head><body><main>
<p><a href="/app/#{escape('journey/' + workflow_id, quote=True)}">← Back to {escape(workflow['display_name'])}</a></p>
<p class="context">{escape(workflow['display_name'])} · Synthetic demo preview</p>
{body}
<section class="caveats"><h2>Use boundaries</h2><ul>{caveat_html}</ul></section>
</main></body></html>"""


def _load_journey(workflow_id: str, path: Path, root: Path) -> dict[str, Any]:
    copy = ADVISOR_WORKFLOW_COPY[workflow_id]
    try:
        workflow = json.loads(path.read_text(encoding="utf-8"))
        if workflow.get("workflow_id") != workflow_id or not isinstance(workflow.get("ordered_steps"), list):
            raise ValueError("invalid workflow")
        steps = [_normalize_step(workflow_id, step, root) for step in workflow["ordered_steps"]]
        if any(
            step["report_id"] in SUPERSEDED_REPORT_IDS and step["step_role"] == "primary"
            for step in steps
        ):
            raise ValueError("superseded primary report")
        return {
            "workflow_id": workflow_id,
            "display_name": copy["display_name"],
            "description": copy["description"],
            "audience": workflow.get("audience", "Advisor review"),
            "core_question": workflow.get("core_user_question", "What should this conversation cover?"),
            "ordered_steps": steps,
            "caveats": list(EXTERNAL_STORY_CAVEATS) if workflow_id == "external_manager_story_translation_v1" else [],
            "available": True,
            "availability_message": "",
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {
            "workflow_id": workflow_id,
            "display_name": copy["display_name"],
            "description": copy["description"],
            "audience": "Advisor review",
            "core_question": "Journey details are temporarily unavailable.",
            "ordered_steps": [],
            "caveats": list(EXTERNAL_STORY_CAVEATS) if workflow_id == "external_manager_story_translation_v1" else [],
            "available": False,
            "availability_message": "This journey is temporarily unavailable. The other advisor workflows remain usable.",
        }


def _normalize_step(workflow_id: str, step: dict[str, Any], root: Path) -> dict[str, Any]:
    required = ("step_number", "report_id", "display_title", "visible_question_answered", "status", "step_role")
    if not all(key in step for key in required):
        raise ValueError("invalid workflow step")
    status = str(step["status"])
    source = step.get("source_mockup_path") or step.get("source_artifact_path")
    preview_url = None
    if status in AVAILABLE_STATUSES and source and _safe_existing_preview_path(root, str(source)):
        preview_url = f"/api/advisor-workflows/{workflow_id}/reports/{step['report_id']}/preview"
    return {
        "step_number": int(step["step_number"]),
        "report_id": str(step["report_id"]),
        "display_title": str(step["display_title"]),
        "question": str(step["visible_question_answered"]),
        "status": status,
        "status_label": _status_label(status),
        "step_role": str(step["step_role"]),
        "role_label": _role_label(str(step["step_role"])),
        "available_now": preview_url is not None,
        "preview_url": preview_url,
        "availability_note": _availability_note(status, preview_url is not None),
    }


def _source_path_for_step(workflow_id: str, report_id: str, root: Path) -> Path:
    workflow_path = root / DEFAULT_WORKFLOW_DIR / WORKFLOW_FILENAMES[workflow_id]
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    step = next((row for row in workflow["ordered_steps"] if row.get("report_id") == report_id), None)
    if not step or step.get("status") not in AVAILABLE_STATUSES:
        raise AdvisorWorkflowError("This report is not available for preview.")
    source = step.get("source_mockup_path") or step.get("source_artifact_path")
    path = _safe_existing_preview_path(root, str(source or ""))
    if path is None:
        raise AdvisorWorkflowError("This report is not available for preview.")
    return path


def _safe_existing_preview_path(root: Path, relative_path: str) -> Path | None:
    candidate_relative = Path(relative_path)
    if candidate_relative.is_absolute() or candidate_relative.suffix.lower() not in {".md", ".json"}:
        return None
    candidate = (root / candidate_relative).resolve()
    allowed = any(candidate == (root / base).resolve() or (root / base).resolve() in candidate.parents for base in PREVIEW_ROOTS)
    return candidate if allowed and candidate.is_file() else None


def _status_label(status: str) -> str:
    return {
        "accepted": "Available",
        "accepted_with_minor_polish": "Available",
        "available": "Available",
        "setup_note": "Available",
        "gated": "Gated",
        "deferred": "Deferred",
    }.get(status, "Planned")


def _role_label(role: str) -> str:
    return {
        "primary": "Core",
        "supporting": "Supporting",
        "setup_readiness": "Readiness",
        "diagnostic": "Diagnostic",
        "handoff": "Handoff",
    }.get(role, role.replace("_", " ").title())


def _availability_note(status: str, preview_available: bool) -> str:
    if status == "gated":
        return "Gated pending approved data or report shape."
    if status == "deferred":
        return "Deferred from the current demo journey."
    if preview_available:
        return "Preview available."
    return "Included in the journey; a preview is not available yet."


def _inline_markdown(value: str) -> str:
    text = escape(value)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def _markdown_body(markdown: str) -> str:
    lines = markdown.splitlines()
    parts: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|?\s*:?-+", lines[index + 1].strip()):
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            if len(rows) >= 2:
                head = "".join(f"<th>{_inline_markdown(cell)}</th>" for cell in rows[0])
                body_rows = "".join("<tr>" + "".join(f"<td>{_inline_markdown(cell)}</td>" for cell in row) + "</tr>" for row in rows[2:])
                parts.append(f"<table><thead><tr>{head}</tr></thead><tbody>{body_rows}</tbody></table>")
            continue
        if line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")), 3)
            parts.append(f"<h{level}>{_inline_markdown(line[level:].strip())}</h{level}>")
        elif line.startswith("- "):
            items = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(f"<li>{_inline_markdown(lines[index].strip()[2:])}</li>")
                index += 1
            parts.append("<ul>" + "".join(items) + "</ul>")
            continue
        else:
            parts.append(f"<p>{_inline_markdown(line)}</p>")
        index += 1
    return "".join(parts)


def _json_body(payload: Any, title: str | None = None) -> str:
    if isinstance(payload, dict):
        parts = [f"<h2>{escape(title)}</h2>" if title else ""]
        for key, value in payload.items():
            if key in HIDDEN_PREVIEW_FIELDS:
                continue
            label = key.replace("_", " ").strip().title()
            if isinstance(value, (dict, list)):
                parts.append(_json_body(value, label))
            elif isinstance(value, bool):
                parts.append(f'<div class="field"><strong>{escape(label)}</strong>{"Yes" if value else "No"}</div>')
            elif value is not None:
                parts.append(f'<div class="field"><strong>{escape(label)}</strong>{escape(str(value))}</div>')
        return "".join(parts)
    if isinstance(payload, list):
        if all(not isinstance(item, (dict, list)) for item in payload):
            items = "".join(f"<li>{escape(str(item))}</li>" for item in payload)
            return (f"<h2>{escape(title)}</h2>" if title else "") + f"<ul>{items}</ul>"
        return (f"<h2>{escape(title)}</h2>" if title else "") + "".join(_json_body(item) for item in payload)
    return f"<p>{escape(str(payload))}</p>"
