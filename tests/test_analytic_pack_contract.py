from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.analytics import load_analytic_pack, load_pack_components, summarize_analytic_pack, validate_pack_shape

PACK_DIR = ROOT / "data" / "analytic_packs" / "arranger_demo_pack_v1"
MANIFEST_PATH = PACK_DIR / "pack_manifest.json"
TEMPLATES_PATH = ROOT / "src" / "arangur" / "report_elements" / "templates.json"
BOUNDARY_DOC = ROOT / "docs" / "architecture" / "arranger_control_plane_boundary_v1.md"
CONTRACT_DOC = ROOT / "docs" / "contracts" / "analytic_pack_contract_v1.md"

EXPECTED_COMPONENTS = {
    "theme_catalog": ("themes", "theme_id"),
    "classification_lens_catalog": ("lenses", "lens_id"),
    "scenario_catalog": ("scenarios", "scenario_id"),
    "scenario_shock_pack": ("scenario_shocks", "shock_id"),
    "data_confidence_rule_catalog": ("rules", "rule_id"),
    "report_analytic_capability_map": ("capabilities", "report_element_id"),
}


class AnalyticPackContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = cls._load_json(MANIFEST_PATH)
        cls.components = {
            component_name: cls._load_json(PACK_DIR / path)
            for component_name, path in cls.manifest["component_paths"].items()
        }

    def test_fixture_pack_directory_and_manifest_exist(self) -> None:
        self.assertTrue(PACK_DIR.exists())
        self.assertTrue(MANIFEST_PATH.exists())
        self.assertEqual("analytic_pack_manifest.v1", self.manifest["schema_version"])
        self.assertEqual("arranger_demo_pack_v1", self.manifest["pack_id"])
        self.assertTrue(self.manifest["synthetic_demo_pack"])

    def test_manifest_references_expected_component_files(self) -> None:
        self.assertEqual(set(EXPECTED_COMPONENTS), set(self.manifest["component_paths"]))
        for component_name, path_value in self.manifest["component_paths"].items():
            with self.subTest(component_name=component_name):
                self.assertFalse(Path(path_value).is_absolute())
                self.assertNotIn("..", Path(path_value).parts)
                self.assertTrue((PACK_DIR / path_value).exists())

    def test_each_component_file_loads_as_json_and_belongs_to_pack(self) -> None:
        for component_name, payload in self.components.items():
            with self.subTest(component_name=component_name):
                self.assertEqual("analytic_pack_component.v1", payload["schema_version"])
                self.assertEqual("arranger_demo_pack_v1", payload["pack_id"])
                self.assertEqual(component_name, payload["component_type"])
                self.assertTrue(payload["synthetic_demo_pack"])

    def test_ids_are_present_and_unique_within_each_component(self) -> None:
        for component_name, (list_key, id_key) in EXPECTED_COMPONENTS.items():
            records = self.components[component_name][list_key]
            ids = [record.get(id_key) for record in records]
            with self.subTest(component_name=component_name):
                self.assertTrue(records)
                self.assertTrue(all(isinstance(record_id, str) and record_id for record_id in ids))
                self.assertEqual(len(ids), len(set(ids)))

    def test_scenario_shocks_reference_valid_scenario_ids(self) -> None:
        scenario_ids = {
            scenario["scenario_id"]
            for scenario in self.components["scenario_catalog"]["scenarios"]
        }
        for shock in self.components["scenario_shock_pack"]["scenario_shocks"]:
            with self.subTest(shock_id=shock["shock_id"]):
                self.assertIn(shock["scenario_id"], scenario_ids)
                self.assertTrue(shock["variable_shocks"])

    def test_demo_pack_has_curated_v1_content_scale(self) -> None:
        self.assertGreaterEqual(len(self.components["theme_catalog"]["themes"]), 10)
        self.assertLessEqual(len(self.components["theme_catalog"]["themes"]), 12)
        self.assertGreaterEqual(len(self.components["scenario_catalog"]["scenarios"]), 5)
        self.assertLessEqual(len(self.components["scenario_catalog"]["scenarios"]), 8)
        self.assertEqual(4, len(self.components["classification_lens_catalog"]["lenses"]))
        self.assertGreaterEqual(len(self.components["data_confidence_rule_catalog"]["rules"]), 5)

    def test_advisor_facing_descriptions_exist(self) -> None:
        for theme in self.components["theme_catalog"]["themes"]:
            with self.subTest(theme_id=theme["theme_id"]):
                self.assertTrue(theme["advisor_description"].strip())
                self.assertTrue(theme["description"].strip())
                self.assertTrue(theme["likely_affected_portfolio_areas"])
        for scenario in self.components["scenario_catalog"]["scenarios"]:
            with self.subTest(scenario_id=scenario["scenario_id"]):
                self.assertTrue(scenario["advisor_story"].strip())
                self.assertTrue(scenario["short_description"].strip())
                self.assertTrue(scenario["likely_affected_portfolio_areas"])

    def test_capability_map_references_current_report_element_ids(self) -> None:
        template_payload = self._load_json(TEMPLATES_PATH)
        current_template_ids = {
            template["element_id"]
            for template in template_payload["templates"]
        }
        capabilities = self.components["report_analytic_capability_map"]["capabilities"]
        for capability in capabilities:
            with self.subTest(report_element_id=capability["report_element_id"]):
                self.assertIn(capability["report_element_id"], current_template_ids)
                self.assertIn("required_inputs", capability)
                self.assertIsInstance(capability["supported_themes"], list)
                self.assertIsInstance(capability["supported_scenarios"], list)
                self.assertIsInstance(capability["supported_lenses"], list)
                self.assertIsInstance(capability["supported_scopes"], list)

    def test_loader_loads_summarizes_and_validates_pack(self) -> None:
        components = load_pack_components(PACK_DIR)
        self.assertEqual(set(EXPECTED_COMPONENTS), set(components))

        loaded = load_analytic_pack(PACK_DIR)
        self.assertEqual("valid", loaded["validation"]["status"])
        self.assertEqual("arranger_demo_pack_v1", loaded["manifest"]["pack_id"])

        summary = summarize_analytic_pack(PACK_DIR)
        self.assertEqual(12, summary["component_counts"]["theme_catalog"])
        self.assertEqual(5, summary["component_counts"]["scenario_catalog"])
        self.assertTrue(summary["synthetic_demo_pack"])

    def test_validator_catches_invalid_scenario_reference(self) -> None:
        scratch = ROOT / "data" / "analytic_packs" / ".test_invalid_pack"
        shutil.rmtree(scratch, ignore_errors=True)
        try:
            copied_pack = scratch / "pack"
            shutil.copytree(PACK_DIR, copied_pack)
            shock_path = copied_pack / "scenario_shock_pack.json"
            payload = self._load_json(shock_path)
            payload["scenario_shocks"][0]["scenario_id"] = "not_a_real_scenario"
            shock_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            validation = validate_pack_shape(copied_pack, template_catalog_path=TEMPLATES_PATH)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

        self.assertEqual("invalid", validation["status"])
        self.assertTrue(
            any(issue["code"] == "SCENARIO_SHOCK_REFERENCE_INVALID" for issue in validation["errors"])
        )

    def test_docs_preserve_control_plane_boundary(self) -> None:
        boundary = BOUNDARY_DOC.read_text(encoding="utf-8").lower()
        contract = CONTRACT_DOC.read_text(encoding="utf-8").lower()
        combined = f"{boundary}\n{contract}"

        self.assertIn("internal", boundary)
        self.assertIn("not advisor-facing", boundary)
        self.assertIn("publish/consume", boundary)
        self.assertIn("advisors select", boundary)
        self.assertIn("approved analytic packs", combined)
        self.assertIn("not a third advisor home menu item", boundary)

    def test_no_control_plane_ui_or_external_dependency_was_added(self) -> None:
        app_static = ROOT / "src" / "arangur" / "app" / "static" / "index.html"
        app_text = app_static.read_text(encoding="utf-8").lower()
        self.assertNotIn("arranger studio", app_text)
        self.assertNotIn("control-plane editor", app_text)
        self.assertFalse((ROOT / "src" / "arangur" / "app" / "analytic_packs.py").exists())

        analytics_source = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (ROOT / "src" / "arangur" / "analytics").glob("*.py")
        )
        for marker in ("import requests", "import httpx", "import pandas", "boto3", "plaid"):
            self.assertNotIn(marker, analytics_source)

    @staticmethod
    def _load_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
