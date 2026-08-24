from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class TelemetrySummary:
    requests: int
    total_latency_ms: float
    llm_calls: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_usd: float


class MetricsCollector:
    """Agregador local y thread-safe para la demostración de observabilidad."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._requests = 0
        self._total_latency_ms = 0.0
        self._llm_calls = 0
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._estimated_cost_usd = 0.0

    def record_request(self, latency_ms: float) -> None:
        with self._lock:
            self._requests += 1
            self._total_latency_ms += latency_ms

    def record_llm_call(self, prompt_tokens: int, completion_tokens: int, cost_usd: float) -> None:
        with self._lock:
            self._llm_calls += 1
            self._prompt_tokens += prompt_tokens
            self._completion_tokens += completion_tokens
            self._estimated_cost_usd += cost_usd

    def summary(self) -> TelemetrySummary:
        with self._lock:
            return TelemetrySummary(
                requests=self._requests,
                total_latency_ms=round(self._total_latency_ms, 2),
                llm_calls=self._llm_calls,
                prompt_tokens=self._prompt_tokens,
                completion_tokens=self._completion_tokens,
                estimated_cost_usd=round(self._estimated_cost_usd, 8),
            )


metrics_collector = MetricsCollector()
