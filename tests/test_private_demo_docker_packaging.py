from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arangur.app.briefing_spec_sets import validate_briefing_spec_set_payload
from arangur.app.settings import load_settings


class PrivateDemoDockerPackagingTests(unittest.TestCase):
    def test_dockerfile_serves_fastapi_app_without_reload(self) -> None:
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("FROM python:", dockerfile)
        self.assertIn("slim", dockerfile)
        self.assertIn("python -m pip install --no-cache-dir -r requirements.txt", dockerfile)
        self.assertIn("PYTHONPATH=/app/src", dockerfile)
        self.assertIn("EXPOSE 8000", dockerfile)
        self.assertIn("arangur.app.main:app", dockerfile)
        self.assertIn("0.0.0.0", dockerfile)
        self.assertNotIn("--reload", dockerfile)

    def test_compose_defines_app_postgres_and_healthchecks(self) -> None:
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("app:", compose)
        self.assertIn("postgres:", compose)
        self.assertIn("build:", compose)
        self.assertIn('"8000:8000"', compose)
        self.assertIn("DB_ENGINE", compose)
        self.assertIn("postgres", compose)
        self.assertIn("DATABASE_URL", compose)
        self.assertIn("service_healthy", compose)
        self.assertIn("pg_isready", compose)
        self.assertIn("/api/health", compose)
        self.assertNotIn("5432:5432", compose)

    def test_private_demo_env_example_is_demo_only(self) -> None:
        env_text = (ROOT / ".env.private-demo.example").read_text(encoding="utf-8")
        env = self._parse_env(env_text)
        self.assertEqual("private_demo", env["APP_ENV"])
        self.assertEqual("http://127.0.0.1:8000", env["PUBLIC_ORIGIN"])
        self.assertEqual("http://127.0.0.1:8000,http://localhost:8000", env["ALLOWED_ORIGINS"])
        self.assertEqual("postgres", env["DB_ENGINE"])
        self.assertEqual("arangur_demo", env["POSTGRES_DB"])
        self.assertEqual("arangur_demo", env["POSTGRES_USER"])
        self.assertEqual("change_me_demo_only", env["POSTGRES_PASSWORD"])
        self.assertIn("@postgres:5432/arangur_demo", env["DATABASE_URL"])
        self.assertNotRegex(env_text, re.compile(r"sk-[A-Za-z0-9]"))
        self.assertNotIn("BEGIN PRIVATE KEY", env_text)
        self.assertNotIn("access_token=", env_text.lower())
        self.assertIn("change_me", env["POSTGRES_PASSWORD"])

    def test_settings_parse_private_demo_docker_env(self) -> None:
        env = self._parse_env((ROOT / ".env.private-demo.example").read_text(encoding="utf-8"))
        settings = load_settings(env)
        self.assertEqual("private_demo", settings.app_env)
        self.assertEqual("private_demo", settings.runtime_mode)
        self.assertEqual("postgres", settings.db_engine)
        self.assertEqual("http://127.0.0.1:8000", settings.public_origin)
        self.assertEqual(("http://127.0.0.1:8000", "http://localhost:8000"), settings.allowed_origins)
        self.assertTrue(settings.database_url_configured)
        self.assertFalse(settings.demo_admin_token_configured)

    def test_dockerignore_excludes_local_secrets_but_keeps_example_env(self) -> None:
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        self.assertIn(".git", dockerignore)
        self.assertIn(".env.*", dockerignore)
        self.assertIn("!.env.private-demo.example", dockerignore)
        self.assertIn("venv/", dockerignore)
        self.assertIn("node_modules/", dockerignore)
        self.assertNotIn("data/", dockerignore)
        self.assertNotIn("reports/", dockerignore)

    def test_private_demo_smoke_script_checks_local_stack_surfaces(self) -> None:
        script_path = ROOT / "scripts" / "private_demo_smoke.cmd"
        self.assertTrue(script_path.exists())
        script = script_path.read_text(encoding="utf-8")
        self.assertIn("curl.exe", script)
        self.assertIn("/api/health", script)
        self.assertIn("/app/", script)
        self.assertIn("/api/report-elements", script)
        self.assertIn("-X POST", script)
        self.assertIn("/api/briefing-spec-sets", script)
        self.assertIn("private_demo_seed_briefing_spec_set.json", script)
        self.assertIn("already be running", script)
        self.assertNotIn("docker compose --env-file .env.private-demo up", script)
        self._assert_no_real_secret_markers(script)

    def test_private_demo_seed_payload_is_valid_synthetic_demo_only(self) -> None:
        payload_path = ROOT / "scripts" / "fixtures" / "private_demo_seed_briefing_spec_set.json"
        self.assertTrue(payload_path.exists())
        payload_text = payload_path.read_text(encoding="utf-8")
        self._assert_no_real_secret_markers(payload_text)
        payload = json.loads(payload_text)
        validation = validate_briefing_spec_set_payload(payload)
        self.assertEqual("arangur.local_briefing_spec_set.v1", validation["schema_version"])
        self.assertTrue(validation["synthetic_data"])
        self.assertEqual(1, validation["client_briefing_set_count"])
        self.assertEqual(1, validation["advisor_review_set_count"])
        self.assertIn("Demo", validation["client_name"])

    def test_private_demo_down_helper_keeps_volume_reset_explicit(self) -> None:
        script_path = ROOT / "scripts" / "private_demo_down.cmd"
        self.assertTrue(script_path.exists())
        script = script_path.read_text(encoding="utf-8")
        self.assertIn("docker compose --env-file .env.private-demo down", script)
        self.assertIn("--reset", script)
        self.assertIn("down -v", script)
        self.assertIn("WARNING", script)
        self.assertIn("choice", script)
        self._assert_no_real_secret_markers(script)

    def test_readme_and_private_demo_docs_reference_smoke_script(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docker_doc = (ROOT / "docs" / "deployment" / "private_demo_docker.md").read_text(encoding="utf-8")
        for text in (readme, docker_doc):
            self.assertIn("scripts\\private_demo_smoke.cmd", text)
            self.assertIn("expects the stack", text)
            self.assertIn("synthetic", text.lower())
            self.assertIn("real client data", text.lower())

    def test_private_demo_walkthrough_exists_and_is_linked(self) -> None:
        walkthrough_path = ROOT / "docs" / "demo" / "private_demo_walkthrough.md"
        self.assertTrue(walkthrough_path.exists())
        walkthrough = walkthrough_path.read_text(encoding="utf-8")
        self.assertIn("copy .env.private-demo.example .env.private-demo", walkthrough)
        self.assertIn("docker compose --env-file .env.private-demo up --build", walkthrough)
        self.assertIn("scripts\\private_demo_smoke.cmd", walkthrough)
        self.assertIn("Advisor Home", walkthrough)
        self.assertIn("Populate a workflow with data", walkthrough)
        self.assertIn("Present / view reports", walkthrough)
        self.assertIn("generated report", walkthrough.lower())
        self.assertIn("no real client data", walkthrough.lower())
        self.assertIn("QA Checklist", walkthrough)
        self.assertIn("Docker stack starts", walkthrough)
        self._assert_no_real_secret_markers(walkthrough)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docker_doc = (ROOT / "docs" / "deployment" / "private_demo_docker.md").read_text(encoding="utf-8")
        for text in (readme, docker_doc):
            self.assertIn("docs/demo/private_demo_walkthrough.md", text)

    def _parse_env(self, env_text: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for line in env_text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            key, value = stripped.split("=", 1)
            parsed[key] = value
        return parsed

    def _assert_no_real_secret_markers(self, text: str) -> None:
        self.assertNotRegex(text, re.compile(r"sk-[A-Za-z0-9]"))
        self.assertNotIn("BEGIN PRIVATE KEY", text)
        self.assertNotIn("access_token=", text.lower())
        self.assertNotIn("client_secret", text.lower())
        self.assertNotIn("api_key", text.lower())


if __name__ == "__main__":
    unittest.main()
