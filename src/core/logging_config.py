import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Emite eventos legibles por personas y herramientas de observabilidad."""

    def format(self, record: logging.LogRecord) -> str:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "event"):
            event["event"] = record.event
        for field in (
            "latency_ms", "prompt_tokens", "completion_tokens", "cost_usd", "model", "status_code", "path", "abstained"
        ):
            if hasattr(record, field):
                event[field] = getattr(record, field)
        return json.dumps(event, ensure_ascii=False)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
