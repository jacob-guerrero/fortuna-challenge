from dataclasses import dataclass

from src.api.schemas.ticket import TicketCreateRequest, TicketResponse
from src.domain.policy_search_port import PolicyChunk, PolicySearchPort
from src.use_cases.clasificar_ticket import ClasificarTicketUseCase


AUTONOMY_SCORE = 0.55


@dataclass(frozen=True)
class OrchestrationResult:
    ticket: TicketResponse
    answer: str
    sources: list[PolicyChunk]
    escalated: bool
    escalation_reason: str | None
    steps: list[str]


class OrquestarSolicitudUseCase:
    """Coordina clasificación, recuperación de evidencia y escalamiento seguro."""

    def __init__(self, classifier: ClasificarTicketUseCase, policies: PolicySearchPort) -> None:
        self._classifier = classifier
        self._policies = policies

    def execute(self, request: TicketCreateRequest) -> OrchestrationResult:
        ticket = self._classifier.ejecutar(request)
        question = f"{request.asunto}. {request.descripcion}"
        candidates = self._policies.search(question, limit=3)
        sources = [chunk for chunk in candidates if chunk.score >= 0.35]
        best_score = max((chunk.score for chunk in sources), default=0.0)

        if not sources:
            return OrchestrationResult(
                ticket=self._with_status(ticket, "Escalado"),
                answer="No encontré evidencia vigente para responder esta solicitud.",
                sources=[],
                escalated=True,
                escalation_reason="Sin evidencia suficiente en las políticas vigentes.",
                steps=["classified", "rag_abstained", "escalated"],
            )

        answer = "\n\n".join(
            f"Según {source.document}, pág. {source.page}, sección {source.section}: {source.content}"
            for source in sources
        )
        if best_score < AUTONOMY_SCORE:
            return OrchestrationResult(
                ticket=self._with_status(ticket, "Escalado"),
                answer=answer,
                sources=sources,
                escalated=True,
                escalation_reason="La evidencia recuperada requiere validación humana.",
                steps=["classified", "rag_retrieved", "drafted_with_citations", "escalated"],
            )

        return OrchestrationResult(
            ticket=ticket,
            answer=answer,
            sources=sources,
            escalated=False,
            escalation_reason=None,
            steps=["classified", "rag_retrieved", "drafted_with_citations"],
        )

    @staticmethod
    def _with_status(ticket: TicketResponse, status: str) -> TicketResponse:
        return ticket.model_copy(update={"estado": status})
