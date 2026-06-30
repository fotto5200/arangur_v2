"""Report-element template catalog for Arangur briefing composition."""

from .catalog import (
    ReportElementCatalogError,
    filter_templates,
    get_template,
    list_templates,
    load_templates,
    validate_template_catalog,
)
from .input_mapping import (
    build_all_demo_report_element_inputs,
    build_report_element_input,
    load_simulation_outputs,
    validate_report_element_input,
    write_demo_report_element_inputs,
)
from .rendering import (
    render_all_demo_report_element_views,
    render_report_element_html,
    render_report_element_markdown,
    render_report_element_view,
    validate_report_element_view,
)

__all__ = [
    "ReportElementCatalogError",
    "build_all_demo_report_element_inputs",
    "build_report_element_input",
    "filter_templates",
    "get_template",
    "list_templates",
    "load_simulation_outputs",
    "load_templates",
    "render_all_demo_report_element_views",
    "render_report_element_html",
    "render_report_element_markdown",
    "render_report_element_view",
    "validate_report_element_input",
    "validate_report_element_view",
    "validate_template_catalog",
    "write_demo_report_element_inputs",
]
