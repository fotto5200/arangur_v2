"""FastAPI application shell for the deployable Arangur v2 demo."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .settings import APP_NAME, AppSettings, load_settings


STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_PATH = STATIC_DIR / "index.html"


def create_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()
    app = FastAPI(
        title="Arangur v2 Demo App",
        description="Private-demo FastAPI shell for the synthetic Arangur v2 workflow.",
        version="0.1.0",
    )
    app.state.settings = resolved_settings

    if resolved_settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(resolved_settings.allowed_origins),
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type"],
        )

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "app": APP_NAME,
            "app_env": resolved_settings.app_env,
            "runtime_mode": resolved_settings.runtime_mode,
            "db_engine": resolved_settings.db_engine,
            "database_configured": resolved_settings.database_url_configured,
            "demo_admin_token_configured": resolved_settings.demo_admin_token_configured,
        }

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/app/", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/app/index.html", response_class=HTMLResponse, include_in_schema=False)
    def demo_console() -> HTMLResponse:
        return HTMLResponse(_index_html())

    return app


def _index_html() -> str:
    return INDEX_PATH.read_text(encoding="utf-8")


app = create_app()
