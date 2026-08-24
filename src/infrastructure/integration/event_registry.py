import hashlib
import json
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class EventReservation:
    is_new: bool
    conflict: bool


class InMemoryEventRegistry:
    """Registro de idempotencia de demostración; reemplazable por tabla SQL."""

    def __init__(self) -> None:
        self._events: dict[str, str] = {}
        self._delivered: set[str] = set()
        self._lock = Lock()

    def reserve(self, event_id: str, payload: dict) -> EventReservation:
        payload_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        with self._lock:
            previous = self._events.get(event_id)
            if previous is None:
                self._events[event_id] = payload_hash
                return EventReservation(is_new=True, conflict=False)
            return EventReservation(is_new=False, conflict=previous != payload_hash)

    def mark_delivered(self, event_id: str) -> None:
        with self._lock:
            self._delivered.add(event_id)

    def was_delivered(self, event_id: str) -> bool:
        with self._lock:
            return event_id in self._delivered

    def clear(self) -> None:
        with self._lock:
            self._events.clear()
            self._delivered.clear()
