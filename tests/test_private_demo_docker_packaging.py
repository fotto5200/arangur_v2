from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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

    def _parse_env(self, env_text: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for line in env_text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            key, value = stripped.split("=", 1)
            parsed[key] = value
        return parsed


if __name__ == "__main__":
    unittest.main()
