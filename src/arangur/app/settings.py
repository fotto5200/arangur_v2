"""Environment-backed settings for the Arangur v2 FastAPI shell."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field


APP_NAME = "arangur_v2"
DEFAULT_APP_ENV = "local"
DEFAULT_DB_ENGINE = "none"


@dataclass(frozen=True)
class AppSettings:
    app_env: str = DEFAULT_APP_ENV
    public_origin: str | None = None
    allowed_origins: tuple[str, ...] = ()
    demo_admin_token: str | None = field(default=None, repr=False)
    db_engine: str = DEFAULT_DB_ENGINE
    database_url: str | None = field(default=None, repr=False)

    @property
    def runtime_mode(self) -> str:
        if self.app_env == "private_demo":
            return "private_demo"
        return "local"

    @property
    def demo_admin_token_configured(self) -> bool:
        return bool(self.demo_admin_token)

    @property
    def database_url_configured(self) -> bool:
        return bool(self.database_url)


def load_settings(environ: Mapping[str, str] | None = None) -> AppSettings:
    env = environ or os.environ
    app_env = _clean_key(env.get("APP_ENV")) or DEFAULT_APP_ENV
    db_engine = _clean_key(env.get("DB_ENGINE")) or DEFAULT_DB_ENGINE
    return AppSettings(
        app_env=app_env,
        public_origin=_clean_value(env.get("PUBLIC_ORIGIN")),
        allowed_origins=_split_csv(env.get("ALLOWED_ORIGINS")),
        demo_admin_token=_clean_value(env.get("DEMO_ADMIN_TOKEN")),
        db_engine=db_engine,
        database_url=_clean_value(env.get("DATABASE_URL")),
    )


def _clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_key(value: str | None) -> str | None:
    cleaned = _clean_value(value)
    if not cleaned:
        return None
    return cleaned.lower()


def _split_csv(value: str | None) -> tuple[str, ...]:
    cleaned = _clean_value(value)
    if not cleaned:
        return ()
    return tuple(part.strip() for part in cleaned.split(",") if part.strip())
