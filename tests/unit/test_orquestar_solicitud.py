from src.api.schemas.ticket import TicketCreateRequest
from src.domain.llm_port import LLMPort
from src.domain.policy_search_port import PolicyChunk, PolicySearchPort
from src.use_cases.clasificar_ticket import ClasificarTicketUseCase
from src.use_cases.orquestar_solicitud import OrquestarSolicitudUseCase


class StubLLM(LLMPort):
    def clasificar_ticket(self, texto: str) -> dict:
        return {"categoria": "Vacaciones", "prioridad": "Media"}


class StubPolicies(PolicySearchPort):
    def __init__(self, chunks: list[PolicyChunk]) -> None:
        self.chunks = chunks

    def search(self, question: str, limit: int) -> list[PolicyChunk]:
        return self.chunks[:limit]


def _request() -> TicketCreateRequest:
    return TicketCreateRequest(
        asunto="Solicitud de vacaciones",
        descripcion="Quiero saber el plazo para solicitar descanso.",
        area="Talento Humano",
        solicitante="persona@empresa.co",
    )


def test_escala_si_rag_no_tiene_evidencia():
    use_case = OrquestarSolicitudUseCase(ClasificarTicketUseCase(StubLLM()), StubPolicies([]))

    result = use_case.execute(_request())

    assert result.escalated is True
    assert result.ticket.estado == "Escalado"
    assert result.steps == ["classified", "rag_abstained", "escalated"]


def test_responde_autonomamente_con_evidencia_fuerte_y_citas():
    chunk = PolicyChunk("Solicite con 15 días.", "vacaciones.pdf", 2, "Solicitud", 0.82)
    use_case = OrquestarSolicitudUseCase(ClasificarTicketUseCase(StubLLM()), StubPolicies([chunk]))

    result = use_case.execute(_request())

    assert result.escalated is False
    assert result.ticket.estado == "Abierto"
    assert "vacaciones.pdf" in result.answer
    assert result.sources == [chunk]
