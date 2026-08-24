from dataclasses import dataclass
from time import perf_counter

from src.domain.policy_search_port import PolicyChunk, PolicySearchPort


ABSTENTION_MESSAGE = "No encontré información vigente para esto."


@dataclass(frozen=True)
class PolicyAnswer:
    answer: str
    sources: list[PolicyChunk]
    abstained: bool
    latency_ms: float


class ConsultarPoliticaUseCase:
    """Recupera evidencia y se abstiene cuando no supera el umbral definido."""

    def __init__(self, repository: PolicySearchPort, minimum_score: float = 0.35) -> None:
        self._repository = repository
        self._minimum_score = minimum_score

    def execute(self, question: str) -> PolicyAnswer:
        started_at = perf_counter()
        candidates = self._repository.search(question, limit=3)
        sources = [chunk for chunk in candidates if chunk.score >= self._minimum_score]
        latency_ms = round((perf_counter() - started_at) * 1000, 2)
        if not sources:
            return PolicyAnswer(ABSTENTION_MESSAGE, [], True, latency_ms)

        excerpts = "\n\n".join(
            f"Según {source.document}, pág. {source.page}, sección {source.section}: {source.content}"
            for source in sources
        )
        return PolicyAnswer(excerpts, sources, False, latency_ms)
