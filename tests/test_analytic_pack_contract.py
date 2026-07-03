from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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

    @staticmethod
    def _load_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
