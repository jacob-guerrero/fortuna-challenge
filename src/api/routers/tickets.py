from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.ticket import TicketCreateRequest, TicketResponse
from src.use_cases.clasificar_ticket import ClasificarTicketUseCase
from src.infrastructure.llm.factory import build_llm_adapter

router = APIRouter(prefix="/tickets", tags=["Tickets"])

# Almacenamiento temporal para la demostración de la Etapa 2.
tickets_db: dict[str, TicketResponse] = {}

def get_clasificar_use_case():
    """
    Fábrica de dependencias. El proveedor se resuelve por configuración;
    las rutas y el caso de uso solo conocen el puerto LLMPort.
    """
    return ClasificarTicketUseCase(build_llm_adapter())

@router.post("/", response_model=TicketResponse, status_code=201)
def crear_solicitud(
    ticket_in: TicketCreateRequest, 
    use_case: ClasificarTicketUseCase = Depends(get_clasificar_use_case)
):
    ticket_out = use_case.ejecutar(ticket_in)
    tickets_db[ticket_out.id] = ticket_out
    return ticket_out

@router.get("/{ticket_id}", response_model=TicketResponse)
def consultar_estado(ticket_id: str):
    if ticket_id not in tickets_db:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return tickets_db[ticket_id]

@router.get("/", response_model=list[TicketResponse])
def listar_tickets(estado: str | None = None, area: str | None = None):
    """Lista solicitudes; los filtros pueden combinarse."""
    resultados = list(tickets_db.values())
    if estado:
        resultados = [t for t in resultados if t.estado.lower() == estado.lower()]
    if area:
        resultados = [t for t in resultados if t.area.lower() == area.lower()]
    return resultados
