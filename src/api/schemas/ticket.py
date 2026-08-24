from pydantic import BaseModel, Field

class TicketCreateRequest(BaseModel):
    asunto: str = Field(..., min_length=5, max_length=200)
    descripcion: str = Field(..., max_length=4000)
    area: str = Field(..., min_length=2, max_length=80)
    solicitante: str = Field(..., min_length=5, max_length=120)

class TicketResponse(BaseModel):
    id: str
    estado: str
    area: str
    categoria: str
    prioridad: str
    respuesta_usuario: str | None = None
    resumen_tecnico: str | None = None
