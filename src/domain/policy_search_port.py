from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyChunk:
    content: str
    document: str
    page: int
    section: str
    score: float


class PolicySearchPort(ABC):
    """Puerto para recuperar evidencia de las políticas vigentes."""

    @abstractmethod
    def search(self, question: str, limit: int) -> list[PolicyChunk]:
        """Devuelve fragmentos ordenados por similitud descendente."""
