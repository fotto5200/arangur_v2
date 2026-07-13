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
BUILTIN_TEMPLATE_COPY = {
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


class BriefingTemplateError(ValueError):
    """Raised when committed built-in template content cannot be resolved safely."""


def list_builtin_briefing_templates(root: Path | None = None) -> dict[str, Any]:
    """Return the four catalog workflows in the ordinary saved-workflow shape."""

    resolved_root = (root or project_root()).resolve()
    workflow_dir = resolved_root / DEFAULT_WORKFLOW_DIR
    templates = [
        _load_template(workflow_id, workflow_dir / WORKFLOW_FILENAMES[workflow_id], resolved_root)
        for workflow_id in WORKFLOW_ORDER
    ]
    return {
        "schema_version": "builtin_briefing_template_catalog.v1",
        "template_count": len(templates),
        "templates": templates,
    }


def render_catalog_report_element(
    workflow_id: str,
    report_id: str,
    root: Path | None = None,
) -> dict[str, Any] | None:
    """Return committed report content in the generated-report element contract."""

    resolved_root = (root or project_root()).resolve()
    workflow_path = resolved_root / DEFAULT_WORKFLOW_DIR / WORKFLOW_FILENAMES.get(workflow_id, "")
    if not workflow_path.is_file():
        return None
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    step = next((row for row in workflow.get("ordered_steps", []) if row.get("report_id") == report_id), None)
    if not step or step.get("status") not in AVAILABLE_STATUSES:
        return None
    source_path = _source_path_for_step(workflow_id, report_id, resolved_root)
    if source_path.suffix.lower() == ".md":
        source_text = source_path.read_text(encoding="utf-8")
        body_html = re.sub(r"^<h1>.*?</h1>", "", _markdown_body(source_text), count=1, flags=re.DOTALL)
        body_text = re.sub(r"^#\s+.*?(?:\r?\n)+", "", source_text, count=1).strip()
    else:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        body_html = _json_body(payload)
        body_text = _json_text(payload)
    return {
        "element_key": f"{workflow_id}:{report_id}",
        "element_id": report_id,
        "element_title": step["display_title"],
        "headline": step["display_title"],
        "summary_text": step["visible_question_answered"],
        "html_fragment": body_html,
        "text_fragment": body_text,
        "source_view_matched": True,
        "synthetic_data": True,
    }


def _load_template(workflow_id: str, path: Path, root: Path) -> dict[str, Any]:
    copy = BUILTIN_TEMPLATE_COPY[workflow_id]
    try:
        workflow = json.loads(path.read_text(encoding="utf-8"))
        if workflow.get("workflow_id") != workflow_id or not isinstance(workflow.get("ordered_steps"), list):
            raise ValueError("invalid workflow")
        if any(
            step["report_id"] in SUPERSEDED_REPORT_IDS and step["step_role"] == "primary"
            for step in workflow["ordered_steps"]
        ):
            raise ValueError("superseded primary report")
        target_branch = _target_branch(workflow_id)
        payload = _workflow_payload(workflow_id, copy["display_name"], workflow["ordered_steps"], target_branch, root)
        return {
            "schema_version": "arangur.local_named_briefing_workflows.v1",
            "id": workflow_id,
            "workflow_id": workflow_id,
            "display_name": copy["display_name"],
            "name": copy["display_name"],
            "description": copy["description"],
            "workflow_type": "Advisor Review Workflow" if target_branch == "advisor" else "Client Briefing Workflow",
            "template_kind": "built_in",
            "is_builtin": True,
            "payload": payload,
            "caveats": list(EXTERNAL_STORY_CAVEATS) if workflow_id == "external_manager_story_translation_v1" else [],
            "available": True,
            "availability_message": "",
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {
            "workflow_id": workflow_id,
            "display_name": copy["display_name"],
            "description": copy["description"],
            "name": copy["display_name"],
            "workflow_type": "Advisor Review Workflow" if _target_branch(workflow_id) == "advisor" else "Client Briefing Workflow",
            "template_kind": "built_in",
            "is_builtin": True,
            "payload": _empty_workflow_payload(copy["display_name"]),
            "caveats": list(EXTERNAL_STORY_CAVEATS) if workflow_id == "external_manager_story_translation_v1" else [],
            "available": False,
            "availability_message": "This built-in template is temporarily unavailable.",
        }


def _target_branch(workflow_id: str) -> str:
    return "advisor" if workflow_id in {"advisor_manager_oversight_v1", "external_manager_story_translation_v1"} else "client"


def _empty_workflow_payload(display_name: str) -> dict[str, Any]:
    return {
        "schema_version": "arangur.local_briefing_spec_set.v1",
        "synthetic_data": True,
        "workflow_name": display_name,
        "client_context": {},
        "client_briefing_set": [],
        "advisor_review_set": [],
    }


def _workflow_payload(
    workflow_id: str,
    display_name: str,
    ordered_steps: list[dict[str, Any]],
    target_branch: str,
    root: Path,
) -> dict[str, Any]:
    payload = _empty_workflow_payload(display_name)
    target_set = "Advisor Review Set" if target_branch == "advisor" else "Client Briefing Set"
    specs = []
    for step in ordered_steps:
        source = step.get("source_mockup_path") or step.get("source_artifact_path")
        preview_available = bool(
            step.get("status") in AVAILABLE_STATUSES and source and _safe_existing_preview_path(root, str(source))
        )
        specs.append(
            {
                "order": int(step["step_number"]),
                "local_spec_id": f"builtin:{workflow_id}:{step['report_id']}",
                "element_kind": "analytic",
                "element_id": step["report_id"],
                "element_title": step["display_title"],
                "target_set": target_set,
                "target_branch": "Advisor Review" if target_branch == "advisor" else "Client Briefing",
                "placement": "Main advisor review" if target_branch == "advisor" else "Main client presentation",
                "advisor_internal_purpose": None,
                "configured_parameters": {},
                "preview_available": preview_available,
                "matched_rendered_view": None,
                "confidence_badge": "catalog_report_available" if preview_available else "not_available",
                "catalog_workflow_id": workflow_id,
                "catalog_status": step["status"],
                "caveat": step.get("caveat", "Synthetic demo content."),
            }
        )
    payload["advisor_review_set" if target_branch == "advisor" else "client_briefing_set"] = specs
    return payload


def _source_path_for_step(workflow_id: str, report_id: str, root: Path) -> Path:
    workflow_path = root / DEFAULT_WORKFLOW_DIR / WORKFLOW_FILENAMES[workflow_id]
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    step = next((row for row in workflow["ordered_steps"] if row.get("report_id") == report_id), None)
    if not step or step.get("status") not in AVAILABLE_STATUSES:
        raise BriefingTemplateError("This report is not available for generation.")
    source = step.get("source_mockup_path") or step.get("source_artifact_path")
    path = _safe_existing_preview_path(root, str(source or ""))
    if path is None:
        raise BriefingTemplateError("This report is not available for generation.")
    return path


def _safe_existing_preview_path(root: Path, relative_path: str) -> Path | None:
    candidate_relative = Path(relative_path)
    if candidate_relative.is_absolute() or candidate_relative.suffix.lower() not in {".md", ".json"}:
        return None
    candidate = (root / candidate_relative).resolve()
    allowed = any(candidate == (root / base).resolve() or (root / base).resolve() in candidate.parents for base in PREVIEW_ROOTS)
    return candidate if allowed and candidate.is_file() else None


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


def _json_text(payload: Any, title: str | None = None) -> str:
    lines: list[str] = [title] if title else []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in HIDDEN_PREVIEW_FIELDS:
                continue
            label = key.replace("_", " ").strip().title()
            if isinstance(value, (dict, list)):
                nested = _json_text(value, label)
                if nested:
                    lines.append(nested)
            elif value is not None:
                lines.append(f"{label}: {'Yes' if value is True else 'No' if value is False else value}")
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, (dict, list)):
                lines.append(_json_text(item))
            else:
                lines.append(f"- {item}")
    elif payload is not None:
        lines.append(str(payload))
    return "\n".join(line for line in lines if line)
