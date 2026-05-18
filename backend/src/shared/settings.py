"""Configuración centralizada — ÚNICA puerta a variables de entorno.

NUNCA llames os.environ directo. Si necesitas una var nueva, agrégala aquí.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Mode ────────────────────────────────────────────────────
    env: Literal["development", "test", "preview", "production"] = "development"
    log_level: str = "INFO"

    # ─── Supabase ────────────────────────────────────────────────
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # ─── Database (vía pooler de Supabase para serverless) ───────
    database_url: str = ""

    # ─── CORS ────────────────────────────────────────────────────
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "tauri://localhost",
            "http://localhost:1420",
            "http://localhost:5173",
        ]
    )

    # ─── External services (lazy — solo cargadas si el context los usa) ─
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    resend_api_key: str = ""
    resend_from_email: str = "noreply@connek.ca"
    resend_from_name: str = "Connek"

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # ─── Observability ───────────────────────────────────────────
    sentry_dsn_backend: str = ""

    # ─── Internal ────────────────────────────────────────────────
    internal_cron_secret: str = "dev-secret-change-me"
    fake_sms_mode: bool = True

    # ─── Derived helpers ─────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def jwt_algorithm(self) -> str:
        return "HS256"  # Supabase JWT default

    @property
    def jwt_audience(self) -> str:
        return "authenticated"  # Supabase JWT audience for logged-in users


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton settings (cached). Tests pueden invalidar con get_settings.cache_clear()."""
    return Settings()


# Conveniencia: `from src.shared.settings import settings`
settings: Settings = get_settings()
