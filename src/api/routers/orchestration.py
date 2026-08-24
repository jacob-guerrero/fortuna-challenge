import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas.orchestration import (
    OrchestrationResponse,
    PolicySourceResponse,
    WebhookEventRequest,
    WebhookEventResponse,
)
from src.infrastructure.external_api.mock_client import MockAPIClient
from src.infrastructure.integration.event_registry import InMemoryEventRegistry
from src.infrastructure.llm.factory import build_llm_adapter
from src.infrastructure.rag.factory import build_policy_search_repository
from src.use_cases.clasificar_ticket import ClasificarTicketUseCase
from src.use_cases.orquestar_solicitud import OrchestrationResult, OrquestarSolicitudUseCase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integraciones", tags=["Integraciones"])
event_registry = InMemoryEventRegistry()


def get_orchestrator() -> OrquestarSolicitudUseCase:
    return OrquestarSolicitudUseCase(
        ClasificarTicketUseCase(build_llm_adapter()), build_policy_search_repository()
    )


def get_outbound_client() -> MockAPIClient:
    return MockAPIClient()


def _response(result: OrchestrationResult) -> OrchestrationResponse:
    return OrchestrationResponse(
        ticket=result.ticket,
        answer=result.answer,
        sources=[PolicySourceResponse(**source.__dict__) for source in result.sources],
        escalated=result.escalated,
        escalation_reason=result.escalation_reason,
        steps=result.steps,
    )


@router.post("/mensajeria/webhook", response_model=WebhookEventResponse, status_code=202)
def receive_messaging_webhook(
    event: WebhookEventRequest,
    orchestrator: OrquestarSolicitudUseCase = Depends(get_orchestrator),
    outbound_client: MockAPIClient = Depends(get_outbound_client),
):
    payload = event.model_dump(mode="json")
    reservation = event_registry.reserve(event.evento_id, payload)
    if reservation.conflict:
        raise HTTPException(status_code=409, detail="evento_id reutilizado con un contenido diferente")
    if not reservation.is_new:
        return WebhookEventResponse(
            evento_id=event.evento_id,
            status="duplicate",
            duplicate=True,
            delivery_pending=not event_registry.was_delivered(event.evento_id),
        )

    result = orchestrator.execute(event.solicitud)
    response = _response(result)
    delivery_pending = False
    try:
        outbound_client.send_webhook_event(
            {
                "evento_id": event.evento_id,
                "tipo": "solicitud.procesada",
                "ticket_id": result.ticket.id,
                "estado": result.ticket.estado,
                "escalated": result.escalated,
            }
        )
        event_registry.mark_delivered(event.evento_id)
    except Exception:
        delivery_pending = True
        logger.exception("La notificación saliente se entregará mediante outbox", extra={"event": "outbound_pending"})

    return WebhookEventResponse(
        evento_id=event.evento_id,
        status="accepted",
        duplicate=False,
        delivery_pending=delivery_pending,
        result=response,
    )
