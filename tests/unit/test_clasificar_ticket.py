from src.api.schemas.ticket import TicketCreateRequest
from src.domain.llm_port import LLMPort
from src.use_cases.clasificar_ticket import ClasificarTicketUseCase


class FailingLLMAdapter(LLMPort):
    def clasificar_ticket(self, texto: str) -> dict:
        raise TimeoutError("El proveedor no respondió")


def test_usa_modo_degradado_si_falla_el_proveedor():
    ticket = TicketCreateRequest(
        asunto="No puedo ingresar al sistema",
        descripcion="El acceso fue bloqueado.",
        area="Tecnología",
        solicitante="usuario@empresa.co",
    )

    result = ClasificarTicketUseCase(FailingLLMAdapter()).ejecutar(ticket)

    assert result.estado == "Abierto"
    assert result.area == "Tecnología"
    assert result.categoria == "Pendiente Clasificación Manual"
    assert result.prioridad == "Media"
