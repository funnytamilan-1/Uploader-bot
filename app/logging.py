import logging
import structlog
from app.config import get_settings

SECRET_KEYS = {"BOT_TOKEN", "API_HASH", "AI_API_KEY", "METADATA_API_KEY", "DATABASE_URL", "REDIS_URL"}

def redact(_, __, event_dict):
    for k in list(event_dict):
        if k.upper() in SECRET_KEYS:
            event_dict[k] = "***REDACTED***"
    return event_dict

def configure_logging():
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="%(message)s")
    structlog.configure(
        processors=[redact, structlog.processors.TimeStamper(fmt="iso"), structlog.processors.JSONRenderer()],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

def get_logger(name: str):
    return structlog.get_logger(name)
