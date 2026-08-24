import uuid
import logging
from src.domain.llm_port import LLMPort
from src.api.schemas.ticket import TicketCreateRequest, TicketResponse

logger = logging.getLogger(__name__)

class ClasificarTicketUseCase:
    """
    Caso de Uso: Recibe los datos de un ticket nuevo, invoca a la IA
    para clasificarlo y maneja el modo degradado si la IA falla.
    """
    def __init__(self, llm_adapter: LLMPort):
        self.llm_adapter = llm_adapter

    def ejecutar(self, ticket: TicketCreateRequest) -> TicketResponse:
        texto_analizar = f"Asunto: {ticket.asunto}. Descripcion: {ticket.descripcion}"
        
        # Modo degradado obligatorio (Punto Crítico #4)
        try:
            logger.info("Solicitando clasificación y respuesta al LLM...")
            resultado_ia = self.llm_adapter.clasificar_ticket(texto_analizar)
            categoria = resultado_ia.get("categoria", "Sin Clasificar")
            prioridad = resultado_ia.get("prioridad", "Media")
            respuesta_usuario = resultado_ia.get("respuesta_usuario")
            resumen_tecnico = resultado_ia.get("resumen_tecnico")
        except Exception as e:
            logger.error(f"Fallo crítico en proveedor de IA. Modo degradado activo. Error: {e}")
            categoria = "Pendiente Clasificación Manual"
            prioridad = "Media" # Asumimos prioridad base por seguridad
            respuesta_usuario = "Lo sentimos, el sistema inteligente de atención no está disponible. Un analista revisará su caso a la brevedad."
            resumen_tecnico = "Sistema degradado por fallo en proveedor LLM."

        return TicketResponse(
            id=f"TK-{str(uuid.uuid4())[:8].upper()}",
            estado="Abierto",
            area=ticket.area,
            categoria=categoria,
            prioridad=prioridad,
            respuesta_usuario=respuesta_usuario,
            resumen_tecnico=resumen_tecnico
        )
