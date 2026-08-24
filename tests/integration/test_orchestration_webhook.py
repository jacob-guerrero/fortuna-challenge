from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routers.orchestration import event_registry, get_orchestrator, get_outbound_client
from src.domain.llm_port import LLMPort
from src.domain.policy_search_port import PolicyChunk, PolicySearchPort
from src.use_cases.clasificar_ticket import ClasificarTicketUseCase
from src.use_cases.orquestar_solicitud import OrquestarSolicitudUseCase


class StubLLM(LLMPort):
    def clasificar_ticket(self, texto: str) -> dict:
        return {"categoria": "Vacaciones", "prioridad": "Media"}


class StubPolicies(PolicySearchPort):
    def search(self, question: str, limit: int) -> list[PolicyChunk]:
        return [PolicyChunk("Solicite con 15 días.", "vacaciones.pdf", 2, "Solicitud", 0.8)]


class RecordingClient:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def send_webhook_event(self, event: dict) -> dict:
        self.events.append(event)
        return {"recibido": True}


recording_client = RecordingClient()
client = TestClient(app)


def setup_function():
    event_registry.clear()
    recording_client.events.clear()
    app.dependency_overrides[get_orchestrator] = lambda: OrquestarSolicitudUseCase(
        ClasificarTicketUseCase(StubLLM()), StubPolicies()
    )
    app.dependency_overrides[get_outbound_client] = lambda: recording_client


def teardown_function():
    app.dependency_overrides.clear()


def test_webhook_es_idempotente_y_notifica_una_sola_vez():
    body = {
        "evento_id": "evt-00001",
        "solicitud": {
            "asunto": "Solicitud de vacaciones",
            "descripcion": "Necesito conocer el plazo.",
            "area": "Talento Humano",
            "solicitante": "persona@empresa.co",
        },
    }

    first = client.post("/integraciones/mensajeria/webhook", json=body)
    duplicate = client.post("/integraciones/mensajeria/webhook", json=body)

    assert first.status_code == 202
    assert first.json()["result"]["escalated"] is False
    assert duplicate.status_code == 202
    assert duplicate.json()["duplicate"] is True
    assert len(recording_client.events) == 1


def test_mismo_evento_con_payload_distinto_es_conflicto():
    body = {
        "evento_id": "evt-00002",
        "solicitud": {
            "asunto": "Solicitud de vacaciones",
            "descripcion": "Necesito conocer el plazo.",
            "area": "Talento Humano",
            "solicitante": "persona@empresa.co",
        },
    }
    client.post("/integraciones/mensajeria/webhook", json=body)
    body["solicitud"]["descripcion"] = "Contenido diferente"

    response = client.post("/integraciones/mensajeria/webhook", json=body)

    assert response.status_code == 409
