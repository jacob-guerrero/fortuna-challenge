from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routers.policies import get_policy_query_use_case
from src.domain.policy_search_port import PolicyChunk, PolicySearchPort
from src.use_cases.consultar_politica import ConsultarPoliticaUseCase


class FakePolicyRepository(PolicySearchPort):
    def search(self, question: str, limit: int) -> list[PolicyChunk]:
        return [PolicyChunk("Evidencia de vacaciones.", "POL-GTH-01_Vacaciones.pdf", 2, "3. Solicitud", 0.9)]


def test_policy_endpoint_returns_cited_answer_without_loading_embeddings():
    app.dependency_overrides[get_policy_query_use_case] = lambda: ConsultarPoliticaUseCase(FakePolicyRepository())
    try:
        response = TestClient(app).post("/politicas/consultas", json={"question": "¿Cómo solicito vacaciones?"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["abstained"] is False
    assert body["sources"] == [
        {"document": "POL-GTH-01_Vacaciones.pdf", "page": 2, "section": "3. Solicitud", "score": 0.9}
    ]
