"""Sentry init + logging estructurado."""
from __future__ import annotations

import logging
import sys

from src.shared.settings import settings


def init_sentry(service_name: str) -> None:
    """Inicializa Sentry si hay DSN configurado. No-op en dev sin DSN."""
    if not settings.sentry_dsn_backend:
        return

    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn_backend,
        environment=settings.env,
        integrations=[StarletteIntegration(), FastApiIntegration()],
        traces_sample_rate=0.1 if settings.is_production else 1.0,
        send_default_pii=False,
    )
    sentry_sdk.set_tag("service", service_name)


def setup_logging() -> None:
    """Logging básico stdout. Para production, considerar JSON structured."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s :: %(message)s",
        stream=sys.stdout,
    )
