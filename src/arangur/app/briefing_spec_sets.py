"""Optional persistence for browser-composed briefing spec sets."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from .persistence import (
    PersistenceError,
    _connect,
    initialize_schema_if_needed,
    persistence_enabled,
)
from .settings import AppSettings


LOCAL_SPEC_SET_SCHEMA_VERSION = "arangur.local_briefing_spec_set.v1"
BRIEFING_SPEC_SET_SOURCE = "browser_composer"
BRIEFING_SPEC_SET_STATUS = "draft"
MAX_SPEC_SET_PAYLOAD_BYTES = 262_144
CLIENT_BRANCH = "client_briefing"
ADVISOR_BRANCH = "advisor_review"
BRANCH_LABELS = {
    CLIENT_BRANCH: "Client Briefing",
    ADVISOR_BRANCH: "Advisor Review",
}
TARGET_SET_LABELS = {
    CLIENT_BRANCH: "Client Briefing Set",
    ADVISOR_BRANCH: "Advisor Review Set",
}
FORBIDDEN_PAYLOAD_MARKERS = (
    "access_token",
    "api_key",
    "bearer ",
    "client_secret",
    "private key",
    "routing number",
    "secret_key",
    "social security",
    "ssn",
)


INSERT_BRIEFING_SPEC_SET_SQL = """
INSERT INTO briefing_spec_set (
    spec_set_id,
    schema_version,
    title,
    client_name,
    portfolio_context,
    synthetic_data,
    source,
    status,
    client_briefing_set_count,
    advisor_review_set_count,
    raw_spec_set_json,
    summary_json,
    created_at,
    updated_at
) VALUES (
    %(spec_set_id)s,
    %(schema_version)s,
    %(title)s,
    %(client_name)s,
    %(portfolio_context)s,
    %(synthetic_data)s,
    %(source)s,
    %(status)s,
    %(client_briefing_set_count)s,
    %(advisor_review_set_count)s,
    %(raw_spec_set_json)s::jsonb,
    %(summary_json)s::jsonb,
    %(created_at)s,
    %(updated_at)s
)
ON CONFLICT (spec_set_id) DO UPDATE SET
    schema_version = EXCLUDED.schema_version,
    title = EXCLUDED.title,
    client_name = EXCLUDED.client_name,
    portfolio_context = EXCLUDED.portfolio_context,
    synthetic_data = EXCLUDED.synthetic_data,
    source = EXCLUDED.source,
    status = EXCLUDED.status,
    client_briefing_set_count = EXCLUDED.client_briefing_set_count,
    advisor_review_set_count = EXCLUDED.advisor_review_set_count,
    raw_spec_set_json = EXCLUDED.raw_spec_set_json,
    summary_json = EXCLUDED.summary_json,
    updated_at = EXCLUDED.updated_at
"""

DELETE_BRIEFING_SPEC_ITEMS_SQL = """
DELETE FROM briefing_spec_item
WHERE spec_set_id = %s
"""

INSERT_BRIEFING_SPEC_ITEM_SQL = """
INSERT INTO briefing_spec_item (
    item_id,
    spec_set_id,
    branch,
    order_index,
    element_id,
    element_title,
    placement,
    advisor_internal_purpose,
    parameters_json,
    matched_view_id,
    preview_available,
    confidence_label,
    raw_spec_json
) VALUES (
    %(item_id)s,
    %(spec_set_id)s,
    %(branch)s,
    %(order_index)s,
    %(element_id)s,
    %(element_title)s,
    %(placement)s,
    %(advisor_internal_purpose)s,
    %(parameters_json)s::jsonb,
    %(matched_view_id)s,
    %(preview_available)s,
    %(confidence_label)s,
    %(raw_spec_json)s::jsonb
)
ON CONFLICT (spec_set_id, branch, order_index) DO UPDATE SET
    element_id = EXCLUDED.element_id,
    element_title = EXCLUDED.element_title,
    placement = EXCLUDED.placement,
    advisor_internal_purpose = EXCLUDED.advisor_internal_purpose,
    parameters_json = EXCLUDED.parameters_json,
    matched_view_id = EXCLUDED.matched_view_id,
    preview_available = EXCLUDED.preview_available,
    confidence_label = EXCLUDED.confidence_label,
    raw_spec_json = EXCLUDED.raw_spec_json
"""

SELECT_BRIEFING_SPEC_SET_SUMMARIES_SQL = """
SELECT
    spec_set_id,
    schema_version,
    title,
    client_name,
    portfolio_context,
    synthetic_data,
    source,
    status,
    client_briefing_set_count,
    advisor_review_set_count,
    summary_json,
    created_at,
    updated_at
FROM briefing_spec_set
ORDER BY updated_at DESC, spec_set_id DESC
"""

SELECT_BRIEFING_SPEC_SET_DETAIL_SQL = """
SELECT
    spec_set_id,
    schema_version,
    title,
    client_name,
    portfolio_context,
    synthetic_data,
    source,
    status,
    client_briefing_set_count,
    advisor_review_set_count,
    raw_spec_set_json,
    summary_json,
    created_at,
    updated_at
FROM briefing_spec_set
WHERE spec_set_id = %s
"""

SELECT_BRIEFING_SPEC_ITEMS_SQL = """
SELECT
    item_id,
    spec_set_id,
    branch,
    order_index,
    element_id,
    element_title,
    placement,
    advisor_internal_purpose,
    parameters_json,
    matched_view_id,
    preview_available,
    confidence_label,
    raw_spec_json
FROM briefing_spec_item
WHERE spec_set_id = %s
ORDER BY branch, order_index
"""

DELETE_BRIEFING_SPEC_SET_SQL = """
DELETE FROM briefing_spec_set
WHERE spec_set_id = %s
RETURNING spec_set_id
"""


class BriefingSpecSetError(ValueError):
    """Raised when briefing spec-set validation or persistence fails."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def validate_briefing_spec_set_payload(payload: Any) -> dict[str, Any]:
    """Validate the browser-local spec-set envelope and return summary fields."""

    if not isinstance(payload, dict):
        raise BriefingSpecSetError("invalid_briefing_spec_set", "Briefing spec-set payload must be a JSON object.")
    try:
        encoded_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise BriefingSpecSetError("invalid_briefing_spec_set", "Briefing spec-set payload must be JSON serializable.") from exc
    if len(encoded_payload.encode("utf-8")) > MAX_SPEC_SET_PAYLOAD_BYTES:
        raise BriefingSpecSetError("invalid_briefing_spec_set", "Briefing spec-set payload is too large for the demo API.")
    marker = _find_forbidden_marker(payload)
    if marker:
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"Briefing spec-set payload contains a forbidden marker: {marker}.",
        )

    schema_version = payload.get("schema_version")
    if not schema_version:
        raise BriefingSpecSetError("invalid_briefing_spec_set", "Briefing spec-set payload requires schema_version.")
    if schema_version != LOCAL_SPEC_SET_SCHEMA_VERSION:
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"Unsupported briefing spec-set schema_version: {schema_version}.",
        )
    if "synthetic_data" not in payload:
        raise BriefingSpecSetError("invalid_briefing_spec_set", "Briefing spec-set payload requires synthetic_data.")
    if payload.get("synthetic_data") is not True:
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            "Only synthetic demo briefing spec sets can be saved by this API.",
        )

    client_context = payload.get("client_context")
    if not isinstance(client_context, dict):
        raise BriefingSpecSetError("invalid_briefing_spec_set", "Briefing spec-set payload requires client_context.")
    client_set = payload.get("client_briefing_set")
    advisor_set = payload.get("advisor_review_set")
    if not isinstance(client_set, list) or not isinstance(advisor_set, list):
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            "Briefing spec-set payload requires client_briefing_set and advisor_review_set lists.",
        )

    _validate_spec_list(client_set, CLIENT_BRANCH)
    _validate_spec_list(advisor_set, ADVISOR_BRANCH)

    client_name = _clean_string(
        client_context.get("client_family")
        or client_context.get("client_name")
        or client_context.get("family")
        or "Demo client"
    )
    portfolio_context = _clean_string(client_context.get("portfolio_context") or "Demo portfolio")
    title = _clean_string(payload.get("title") or f"{client_name} briefing spec set")
    return {
        "schema_version": schema_version,
        "title": title,
        "client_name": client_name,
        "portfolio_context": portfolio_context,
        "synthetic_data": True,
        "source": _clean_string(payload.get("source") or BRIEFING_SPEC_SET_SOURCE),
        "status": _clean_string(payload.get("status") or BRIEFING_SPEC_SET_STATUS),
        "client_briefing_set_count": len(client_set),
        "advisor_review_set_count": len(advisor_set),
        "client_context": client_context,
    }


def save_briefing_spec_set(settings: AppSettings | None, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and optionally persist a browser-composed briefing spec set."""

    validation = validate_briefing_spec_set_payload(payload)
    if not persistence_enabled(settings):
        return {
            "persistence_configured": False,
            "saved": False,
            "message": "Backend persistence is not configured. Use local export/download for now.",
            "spec_set": _summary_from_validation(validation),
        }

    try:
        initialize_schema_if_needed(settings)
        spec_set_id = _new_spec_set_id()
        record = briefing_spec_set_record_from_payload(payload, spec_set_id=spec_set_id, validation=validation)
        item_records = briefing_spec_item_records_from_payload(payload, spec_set_id)
        with _connect(settings) as connection:
            with connection.cursor() as cursor:
                cursor.execute(INSERT_BRIEFING_SPEC_SET_SQL, record)
                cursor.execute(DELETE_BRIEFING_SPEC_ITEMS_SQL, (spec_set_id,))
                for item_record in item_records:
                    cursor.execute(INSERT_BRIEFING_SPEC_ITEM_SQL, item_record)
        return {
            "persistence_configured": True,
            "saved": True,
            "message": "Saved briefing spec set.",
            "spec_set": _summary_from_record(record),
        }
    except PersistenceError:
        raise
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not save briefing spec set: {exc}") from exc


def list_briefing_spec_sets(settings: AppSettings | None) -> list[dict[str, Any]]:
    """Return saved briefing spec-set summaries, or an empty list when disabled."""

    if not persistence_enabled(settings):
        return []
    try:
        initialize_schema_if_needed(settings)
        with _connect(settings, dict_rows=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(SELECT_BRIEFING_SPEC_SET_SUMMARIES_SQL)
                return [_summary_from_record(row) for row in cursor.fetchall()]
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not list briefing spec sets: {exc}") from exc


def get_briefing_spec_set(settings: AppSettings | None, spec_set_id: str) -> dict[str, Any] | None:
    """Return one saved spec set with its original payload, or None."""

    if not persistence_enabled(settings):
        return None
    try:
        initialize_schema_if_needed(settings)
        with _connect(settings, dict_rows=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(SELECT_BRIEFING_SPEC_SET_DETAIL_SQL, (spec_set_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                cursor.execute(SELECT_BRIEFING_SPEC_ITEMS_SQL, (spec_set_id,))
                item_rows = list(cursor.fetchall())
        return {
            "persistence_configured": True,
            "spec_set": _summary_from_record(row),
            "payload": _json_value(row["raw_spec_set_json"]),
            "items": [_item_summary_from_record(item_row) for item_row in item_rows],
        }
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not read briefing spec set: {exc}") from exc


def delete_briefing_spec_set(settings: AppSettings | None, spec_set_id: str) -> bool:
    """Delete a saved briefing spec set when persistence is configured."""

    if not persistence_enabled(settings):
        return False
    try:
        initialize_schema_if_needed(settings)
        with _connect(settings) as connection:
            with connection.cursor() as cursor:
                cursor.execute(DELETE_BRIEFING_SPEC_SET_SQL, (spec_set_id,))
                return cursor.fetchone() is not None
    except Exception as exc:  # pragma: no cover - exercised only with live Postgres failures.
        raise PersistenceError(f"Could not delete briefing spec set: {exc}") from exc


def briefing_spec_set_record_from_payload(
    payload: dict[str, Any],
    spec_set_id: str | None = None,
    validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validation = validation or validate_briefing_spec_set_payload(payload)
    resolved_spec_set_id = spec_set_id or _new_spec_set_id()
    now = _now_iso()
    summary = {
        "client_context": validation["client_context"],
        "demo_caveat": "Synthetic browser-composer draft; not a generated report.",
        "item_counts": {
            "client_briefing_set": validation["client_briefing_set_count"],
            "advisor_review_set": validation["advisor_review_set_count"],
        },
    }
    return {
        "spec_set_id": resolved_spec_set_id,
        "schema_version": validation["schema_version"],
        "title": validation["title"],
        "client_name": validation["client_name"],
        "portfolio_context": validation["portfolio_context"],
        "synthetic_data": validation["synthetic_data"],
        "source": validation["source"],
        "status": validation["status"],
        "client_briefing_set_count": validation["client_briefing_set_count"],
        "advisor_review_set_count": validation["advisor_review_set_count"],
        "raw_spec_set_json": _json_dumps(payload),
        "summary_json": _json_dumps(summary),
        "created_at": now,
        "updated_at": now,
    }


def briefing_spec_item_records_from_payload(payload: dict[str, Any], spec_set_id: str) -> list[dict[str, Any]]:
    validate_briefing_spec_set_payload(payload)
    records: list[dict[str, Any]] = []
    for branch, key in ((CLIENT_BRANCH, "client_briefing_set"), (ADVISOR_BRANCH, "advisor_review_set")):
        for index, item in enumerate(payload[key], start=1):
            records.append(briefing_spec_item_record_from_payload_item(item, spec_set_id, branch, index))
    return records


def briefing_spec_item_record_from_payload_item(
    item: dict[str, Any],
    spec_set_id: str,
    branch: str,
    default_order_index: int,
) -> dict[str, Any]:
    matched_view = item.get("matched_rendered_view") if isinstance(item.get("matched_rendered_view"), dict) else {}
    parameters = item.get("configured_parameters") if isinstance(item.get("configured_parameters"), dict) else {}
    order_index = default_order_index
    return {
        "item_id": f"{spec_set_id}_{branch}_{order_index}",
        "spec_set_id": spec_set_id,
        "branch": branch,
        "order_index": order_index,
        "element_id": _clean_optional_string(item.get("element_id")),
        "element_title": _clean_optional_string(item.get("element_title")) or _clean_optional_string(item.get("title")),
        "placement": _clean_optional_string(item.get("placement")),
        "advisor_internal_purpose": _clean_optional_string(item.get("advisor_internal_purpose")),
        "parameters_json": _json_dumps(parameters),
        "matched_view_id": _clean_optional_string(matched_view.get("view_id")),
        "preview_available": bool(item.get("preview_available")),
        "confidence_label": _clean_optional_string(item.get("confidence_badge")),
        "raw_spec_json": _json_dumps(item),
    }


def _validate_spec_list(items: list[Any], branch: str) -> None:
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise BriefingSpecSetError(
                "invalid_briefing_spec_set",
                f"{TARGET_SET_LABELS[branch]} item {index} must be a JSON object.",
            )
        _validate_spec_item(item, branch, index)


def _validate_spec_item(item: dict[str, Any], branch: str, index: int) -> None:
    kind = item.get("element_kind") or "analytic"
    if kind not in {"analytic", "narrative"}:
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"{TARGET_SET_LABELS[branch]} item {index} has unsupported element_kind.",
        )
    target_set = item.get("target_set")
    if target_set and target_set != TARGET_SET_LABELS[branch]:
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"{TARGET_SET_LABELS[branch]} item {index} has the wrong target_set.",
        )
    target_branch = item.get("target_branch")
    if target_branch and target_branch != BRANCH_LABELS[branch]:
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"{TARGET_SET_LABELS[branch]} item {index} has the wrong target_branch.",
        )
    configured_parameters = item.get("configured_parameters", {})
    if configured_parameters is not None and not isinstance(configured_parameters, dict):
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"{TARGET_SET_LABELS[branch]} item {index} configured_parameters must be a JSON object.",
        )
    matched_view = item.get("matched_rendered_view")
    if matched_view is not None and not isinstance(matched_view, dict):
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"{TARGET_SET_LABELS[branch]} item {index} matched_rendered_view must be an object or null.",
        )
    if kind == "narrative":
        if not (_clean_optional_string(item.get("narrative_type")) or _clean_optional_string(item.get("element_title"))):
            raise BriefingSpecSetError(
                "invalid_briefing_spec_set",
                f"{TARGET_SET_LABELS[branch]} narrative item {index} needs a narrative_type or element_title.",
            )
        narrative_fields = item.get("narrative_fields", {})
        if narrative_fields is not None and not isinstance(narrative_fields, dict):
            raise BriefingSpecSetError(
                "invalid_briefing_spec_set",
                f"{TARGET_SET_LABELS[branch]} narrative item {index} narrative_fields must be a JSON object.",
            )
        return
    if not _clean_optional_string(item.get("element_id")):
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"{TARGET_SET_LABELS[branch]} analytic item {index} needs element_id.",
        )
    if not _clean_optional_string(item.get("element_title")):
        raise BriefingSpecSetError(
            "invalid_briefing_spec_set",
            f"{TARGET_SET_LABELS[branch]} analytic item {index} needs element_title.",
        )


def _summary_from_validation(validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "spec_set_id": None,
        "schema_version": validation["schema_version"],
        "title": validation["title"],
        "client_name": validation["client_name"],
        "portfolio_context": validation["portfolio_context"],
        "synthetic_data": validation["synthetic_data"],
        "source": validation["source"],
        "status": validation["status"],
        "client_briefing_set_count": validation["client_briefing_set_count"],
        "advisor_review_set_count": validation["advisor_review_set_count"],
        "created_at": None,
        "updated_at": None,
    }


def _summary_from_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "spec_set_id": record["spec_set_id"],
        "schema_version": record["schema_version"],
        "title": record["title"],
        "client_name": record["client_name"],
        "portfolio_context": record["portfolio_context"],
        "synthetic_data": bool(record["synthetic_data"]),
        "source": record["source"],
        "status": record["status"],
        "client_briefing_set_count": int(record["client_briefing_set_count"] or 0),
        "advisor_review_set_count": int(record["advisor_review_set_count"] or 0),
        "summary": _json_value(record.get("summary_json")),
        "created_at": _json_safe_datetime(record.get("created_at")),
        "updated_at": _json_safe_datetime(record.get("updated_at")),
    }


def _item_summary_from_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": record["item_id"],
        "spec_set_id": record["spec_set_id"],
        "branch": record["branch"],
        "order_index": record["order_index"],
        "element_id": record["element_id"],
        "element_title": record["element_title"],
        "placement": record["placement"],
        "advisor_internal_purpose": record["advisor_internal_purpose"],
        "parameters": _json_value(record.get("parameters_json")),
        "matched_view_id": record["matched_view_id"],
        "preview_available": bool(record["preview_available"]),
        "confidence_label": record["confidence_label"],
    }


def _find_forbidden_marker(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            marker = _find_forbidden_marker(str(key))
            if marker:
                return marker
            marker = _find_forbidden_marker(item)
            if marker:
                return marker
    elif isinstance(value, list):
        for item in value:
            marker = _find_forbidden_marker(item)
            if marker:
                return marker
    elif isinstance(value, str):
        lowered = value.lower()
        for marker in FORBIDDEN_PAYLOAD_MARKERS:
            if marker in lowered:
                return marker.strip()
    return None


def _json_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_safe_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _clean_string(value: Any) -> str:
    cleaned = _clean_optional_string(value)
    return cleaned or ""


def _clean_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _new_spec_set_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"briefing_spec_set_{timestamp}_{uuid.uuid4().hex[:8]}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
