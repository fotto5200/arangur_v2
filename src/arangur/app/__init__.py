"""FastAPI shell for the deployable Arangur v2 demo app."""

from .main import app, create_app
from .settings import APP_NAME, AppSettings, load_settings

__all__ = [
    "APP_NAME",
    "AppSettings",
    "app",
    "create_app",
    "load_settings",
]
