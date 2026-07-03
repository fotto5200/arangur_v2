"""Report-element template catalog for Arangur briefing composition."""

from .catalog import (
    ReportElementCatalogError,
    filter_templates,
    get_template,
    list_templates,
    load_templates,
    validate_template_catalog,
)
from .briefing_set_preview import (
    build_default_advisor_review_set_preview,
    build_default_client_briefing_set_preview,
    load_report_element_views,
    render_briefing_set_preview_html,
    render_briefing_set_preview_markdown,
    validate_briefing_set_preview,
    write_demo_briefing_set_previews,
)
from .generated_report_artifact import (
    build_generated_report_artifact_from_briefing_preview,
    create_demo_generated_report_artifact,
    validate_generated_report_artifact,
    write_demo_generated_report_artifacts,
)
from .input_mapping import (
    build_all_demo_report_element_inputs,
    build_report_element_input,
    load_simulation_outputs,
    validate_report_element_input,
    write_demo_report_element_inputs,
)
from .analytic_input_mapping import (
    build_all_analytic_report_element_inputs,
    build_analytic_report_element_input,
    load_analytic_outputs,
    write_analytic_report_element_inputs,
)
from .rendering import (
    render_all_analytic_report_element_views,
    render_all_demo_report_element_views,
    render_report_element_html,
    render_report_element_markdown,
    render_report_element_view,
    validate_report_element_view,
)

__all__ = [
    "ReportElementCatalogError",
    "build_all_analytic_report_element_inputs",
    "build_all_demo_report_element_inputs",
    "build_default_advisor_review_set_preview",
    "build_default_client_briefing_set_preview",
    "build_generated_report_artifact_from_briefing_preview",
    "build_analytic_report_element_input",
    "build_report_element_input",
    "create_demo_generated_report_artifact",
    "filter_templates",
    "get_template",
    "list_templates",
    "load_analytic_outputs",
    "load_report_element_views",
    "load_simulation_outputs",
    "load_templates",
    "render_briefing_set_preview_html",
    "render_briefing_set_preview_markdown",
    "render_all_analytic_report_element_views",
    "render_all_demo_report_element_views",
    "render_report_element_html",
    "render_report_element_markdown",
    "render_report_element_view",
    "validate_briefing_set_preview",
    "validate_generated_report_artifact",
    "validate_report_element_input",
    "validate_report_element_view",
    "validate_template_catalog",
    "write_demo_briefing_set_previews",
    "write_demo_generated_report_artifacts",
    "write_analytic_report_element_inputs",
    "write_demo_report_element_inputs",
]
