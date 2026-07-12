from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.analytics.report_workflow_catalog import (
    DEFAULT_EXTERNAL_PACK_DIR,
    DEFAULT_WORKFLOW_DIR,
    WORKFLOW_FILENAMES,
    generate_report_workflow_catalog,
    validate_catalog,
)


DOC_PATHS = [
    ROOT / "docs" / "product" / "report_workflow_catalog_v1.md",
    ROOT / "docs" / "product" / "demo_report_suite_v1.md",
    ROOT / "docs" / "product" / "report_family_acceptance_status_v1.md",
    ROOT / "docs" / "product" / "external_manager_story_workflow_v1.md",
]

REQUIRED_WORKFLOW_IDS = {
    "principal_family_office_briefing_minimal_v1",
    "engaged_client_investment_committee_review_v1",
    "advisor_manager_oversight_v1",
    "external_manager_story_translation_v1",
}


class ReportWorkflowCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scratch = ROOT / "data" / "simulation" / ".test_report_workflow_catalog"
        shutil.rmtree(cls.scratch, ignore_errors=True)
        cls.generated = generate_report_workflow_catalog(
            workflow_dir=cls.scratch / "workflows",
            external_pack_dir=cls.scratch / "external_story_pack",
            docs_dir=cls.scratch / "docs",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def test_module_command_generates_scratch_outputs(self) -> None:
        command_dir = self.scratch / "command"
        shutil.rmtree(command_dir, ignore_errors=True)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "arangur.analytics.report_workflow_catalog",
                "--workflow-dir",
                str(command_dir / "workflows"),
                "--external-pack-dir",
                str(command_dir / "external_story_pack"),
                "--docs-dir",
                str(command_dir / "docs"),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Report workflow count: 4", result.stdout)
        self.assertIn("external_manager_story_translation_v1", result.stdout)
        self.assertTrue(
            (command_dir / "workflows" / "report_workflow_catalog_manifest.json").exists()
        )
        self.assertTrue(
            (
                command_dir
                / "external_story_pack"
                / "external_story_translation_manifest.json"
            ).exists()
        )

    def test_workflow_manifest_exists_and_declares_exact_required_workflows(self) -> None:
        manifest = _load_json(DEFAULT_WORKFLOW_DIR / "report_workflow_catalog_manifest.json")

        self.assertEqual("report_workflow_catalog_manifest.v1", manifest["schema_version"])
        self.assertEqual("demo_report_workflows_v1", manifest["catalog_id"])
        self.assertTrue(manifest["synthetic_data"])
        self.assertTrue(manifest["not_wired_to_ui"])
        self.assertTrue(manifest["not_production_reporting"])
        self.assertEqual(4, manifest["workflow_count"])
        self.assertEqual(
            REQUIRED_WORKFLOW_IDS,
            {workflow["workflow_id"] for workflow in manifest["workflows"]},
        )
        self.assertEqual(REQUIRED_WORKFLOW_IDS, set(WORKFLOW_FILENAMES))
        for filename in WORKFLOW_FILENAMES.values():
            with self.subTest(filename=filename):
                self.assertTrue((DEFAULT_WORKFLOW_DIR / filename).exists())

    def test_each_workflow_has_ordered_steps_and_required_shape(self) -> None:
        validation = validate_catalog()
        self.assertEqual("pass", validation["status"])
        self.assertEqual(4, validation["workflow_count"])

        for workflow_id, filename in WORKFLOW_FILENAMES.items():
            workflow = _load_json(DEFAULT_WORKFLOW_DIR / filename)
            with self.subTest(workflow_id=workflow_id):
                self.assertEqual(workflow_id, workflow["workflow_id"])
                self.assertTrue(workflow["ordered_steps"])
                self.assertTrue(workflow["synthetic_data"])
                self.assertTrue(workflow["not_production_recommendation"])
                self.assertIn("supporting_reports", workflow)
                self.assertIn("setup_or_readiness_notes", workflow)
                self.assertIn("diagnostic_reports", workflow)
                self.assertIn("superseded_reports_excluded", workflow)
                self.assertIn("gated_or_deferred_reports", workflow)
                self.assertEqual(
                    list(range(1, len(workflow["ordered_steps"]) + 1)),
                    [step["step_number"] for step in workflow["ordered_steps"]],
                )

    def test_principal_workflow_avoids_dense_attribution_as_primary_steps(self) -> None:
        workflow = _workflow("principal_family_office_briefing_minimal_v1")
        primary_ids = {
            step["report_id"]
            for step in workflow["ordered_steps"]
            if step["step_role"] == "primary"
        }

        self.assertIn("portfolio_representation_status", primary_ids)
        self.assertIn("cash_flow_delivered", primary_ids)
        self.assertIn("cash_flow_support_outlook", primary_ids)
        self.assertNotIn("advisor_policy_attribution_by_manager", primary_ids)
        self.assertNotIn("manager_driver_attribution_matrix", primary_ids)
        self.assertNotIn("within_manager_attribution_detail", primary_ids)
        self.assertTrue(
            any(
                step["report_id"] == "high_level_advisor_plan_next_year_positioning"
                and step["status"] == "gated"
                for step in workflow["ordered_steps"]
            )
        )

    def test_engaged_client_workflow_includes_high_level_attribution_and_exposure(self) -> None:
        workflow = _workflow("engaged_client_investment_committee_review_v1")
        step_ids = {step["report_id"] for step in workflow["ordered_steps"]}

        self.assertIn("advisor_policy_attribution_by_manager", step_ids)
        self.assertIn("manager_mandate_attribution_summary", step_ids)
        self.assertIn("full_lens_exposure_ai_adoption", step_ids)
        self.assertIn("full_lens_exposure_energy_security", step_ids)
        matrix_step = _step_by_id(workflow, "manager_driver_attribution_matrix")
        self.assertEqual("supporting", matrix_step["step_role"])
        self.assertIn(matrix_step["audience_visibility"], {"advisor_review", "advisor_only"})
        self.assertNotIn("within_manager_attribution_detail", step_ids)

    def test_advisor_oversight_workflow_includes_matrix_detail_and_handoff(self) -> None:
        workflow = _workflow("advisor_manager_oversight_v1")
        step_ids = {step["report_id"] for step in workflow["ordered_steps"]}

        self.assertIn("manager_driver_attribution_matrix", step_ids)
        self.assertIn("within_manager_attribution_detail", step_ids)
        self.assertIn("manager_implementation_handoff", step_ids)
        self.assertEqual("advisor_only_diagnostic_workflow", workflow["advisor_only_status"])
        self.assertEqual("gated", _step_by_id(workflow, "coverage_confidence_by_manager")["status"])

    def test_external_story_workflow_includes_story_lenses_scenarios_and_caveats(self) -> None:
        workflow = _workflow("external_manager_story_translation_v1")
        step_ids = {step["report_id"] for step in workflow["ordered_steps"]}

        self.assertIn("external_manager_story_summary", step_ids)
        self.assertIn("external_story_implied_lenses", step_ids)
        self.assertIn("external_story_key_price_scenarios", step_ids)
        self.assertIn("external_story_governance_caveat_note", step_ids)
        self.assertEqual("gated", _step_by_id(workflow, "portfolio_through_external_lens")["status"])
        self.assertEqual("gated", _step_by_id(workflow, "scenario_by_lens_external_story")["status"])
        for step in workflow["ordered_steps"]:
            if step["report_id"].startswith("external_story") or step["report_id"] == "external_manager_story_summary":
                self.assertIn("not verified", step["caveat"].lower())
                self.assertIn("not a recommendation", step["caveat"].lower())

    def test_accepted_report_references_have_existing_mockup_and_view_paths(self) -> None:
        for workflow_id, filename in WORKFLOW_FILENAMES.items():
            workflow = _load_json(DEFAULT_WORKFLOW_DIR / filename)
            for step in workflow["ordered_steps"]:
                with self.subTest(workflow_id=workflow_id, report_id=step["report_id"]):
                    if step["status"] in {
                        "accepted",
                        "accepted_with_minor_polish",
                        "available",
                    }:
                        self.assertTrue((ROOT / step["source_mockup_path"]).exists())
                        self.assertTrue((ROOT / step["source_view_path"]).exists())
                    if step["status"] in {"gated", "deferred"}:
                        self.assertNotIn("source_mockup_path", step)
                        self.assertNotIn("source_view_path", step)

    def test_superseded_and_equal_weight_diagnostic_reports_are_not_primary_policy(self) -> None:
        for workflow_id, filename in WORKFLOW_FILENAMES.items():
            workflow = _load_json(DEFAULT_WORKFLOW_DIR / filename)
            for step in workflow["ordered_steps"]:
                with self.subTest(workflow_id=workflow_id, report_id=step["report_id"]):
                    if step["step_role"] == "primary":
                        self.assertNotIn("policy_level_attribution_summary_v1", step["report_id"])
                        self.assertNotIn("policy_level_manager_effect_detail_v1", step["report_id"])
                        self.assertNotIn("equal_weight", step["report_id"])

        acceptance_doc = (
            ROOT / "docs" / "product" / "report_family_acceptance_status_v1.md"
        ).read_text(encoding="utf-8").lower()
        self.assertIn("diagnostic unless explicitly selected as policy", acceptance_doc)

    def test_external_story_pack_flags_and_artifacts_exist(self) -> None:
        manifest = _load_json(DEFAULT_EXTERNAL_PACK_DIR / "external_story_translation_manifest.json")
        story = _load_json(DEFAULT_EXTERNAL_PACK_DIR / "manager_story_summary.json")
        lenses = _load_json(DEFAULT_EXTERNAL_PACK_DIR / "implied_lenses.json")
        scenarios = _load_json(DEFAULT_EXTERNAL_PACK_DIR / "key_price_scenario_set.json")
        caveats = _load_json(DEFAULT_EXTERNAL_PACK_DIR / "governance_caveats.json")

        self.assertTrue(manifest["translate_do_not_endorse"])
        self.assertTrue(manifest["not_verified"])
        self.assertTrue(manifest["not_recommendation"])
        self.assertEqual("synthetic_demo_translation", manifest["approval_status"])
        self.assertTrue(story["not_verified"])
        self.assertTrue(story["not_recommendation"])
        self.assertGreaterEqual(len(lenses["lenses"]), 6)
        self.assertGreaterEqual(len(scenarios["scenarios"]), 5)
        self.assertTrue(caveats["caveats"]["translate_do_not_endorse"])
        self.assertTrue(caveats["caveats"]["requires_review_before_client_use"])
        for filename in manifest["generated_artifacts"]:
            with self.subTest(filename=filename):
                self.assertTrue((DEFAULT_EXTERNAL_PACK_DIR / filename).exists())

    def test_candidate_proxy_rows_require_approval_and_are_not_recommendations(self) -> None:
        proxies = _load_json(DEFAULT_EXTERNAL_PACK_DIR / "candidate_benchmark_proxy_map.json")

        self.assertTrue(proxies["candidate_proxy_rows"])
        for row in proxies["candidate_proxy_rows"]:
            with self.subTest(row=row["lens_id"]):
                self.assertTrue(row["requires_approval"])
                self.assertTrue(row["not_recommendation"])
                self.assertTrue(row["synthetic_candidate_only"])

    def test_product_docs_exist(self) -> None:
        for path in DOC_PATHS:
            with self.subTest(path=path):
                self.assertTrue(path.exists())
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("TODO", text)
                self.assertNotIn("TBD", text)

    def test_no_docker_or_deployment_files_changed(self) -> None:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        changed = [
            line[3:].strip().replace("\\", "/")
            for line in result.stdout.splitlines()
            if line.strip()
        ]
        forbidden_prefixes = (
            "docs/deployment/",
        )
        forbidden_exact = {
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore",
            "src/arangur/app.py",
            "templates.json",
        }
        for path in changed:
            with self.subTest(path=path):
                self.assertFalse(path.startswith(forbidden_prefixes))
                self.assertNotIn(path, forbidden_exact)


def _workflow(workflow_id: str) -> dict:
    return _load_json(DEFAULT_WORKFLOW_DIR / WORKFLOW_FILENAMES[workflow_id])


def _step_by_id(workflow: dict, report_id: str) -> dict:
    for step in workflow["ordered_steps"]:
        if step["report_id"] == report_id:
            return step
    raise AssertionError(f"Missing step {report_id}")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
