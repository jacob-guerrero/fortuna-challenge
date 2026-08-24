from pydantic import BaseModel, Field

from src.api.schemas.ticket import TicketCreateRequest, TicketResponse


class PolicySourceResponse(BaseModel):
    document: str
    page: int
    section: str
    score: float


class OrchestrationResponse(BaseModel):
    ticket: TicketResponse
    answer: str
    sources: list[PolicySourceResponse]
    escalated: bool
    escalation_reason: str | None
    steps: list[str]


class WebhookEventRequest(BaseModel):
    evento_id: str = Field(..., min_length=8, max_length=128)
    tipo: str = Field("solicitud.recibida", min_length=3, max_length=80)
    solicitud: TicketCreateRequest


class WebhookEventResponse(BaseModel):
    evento_id: str
    status: str
    duplicate: bool
    delivery_pending: bool
    result: OrchestrationResponse | None = None
