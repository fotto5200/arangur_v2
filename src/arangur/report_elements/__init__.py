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

__all__ = [
    "ReportElementCatalogError",
    "build_all_demo_report_element_inputs",
    "build_report_element_input",
    "filter_templates",
    "get_template",
    "list_templates",
    "load_simulation_outputs",
    "load_templates",
    "validate_report_element_input",
    "validate_template_catalog",
    "write_demo_report_element_inputs",
]
