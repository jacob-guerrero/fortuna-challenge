from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routers.tickets import tickets_db

client = TestClient(app)


def setup_function():
    tickets_db.clear()


def test_crear_consultar_y_filtrar_tickets():
    response = client.post(
        "/tickets/",
        json={
            "asunto": "El teclado no responde",
            "descripcion": "Falla desde esta mañana.",
            "area": "Tecnología",
            "solicitante": "usuario@empresa.co",
        },
    )

    assert response.status_code == 201
    ticket = response.json()
    assert ticket["categoria"] == "Hardware"
    assert client.get(f"/tickets/{ticket['id']}").status_code == 200
    assert client.get("/tickets/?estado=Abierto&area=Tecnología").json() == [ticket]


def test_errores_tienen_un_contrato_uniforme():
    not_found = client.get("/tickets/no-existe")
    invalid = client.post("/tickets/", json={"asunto": "x"})

    for response, status, error in ((not_found, 404, "not_found"), (invalid, 422, "validation_error")):
        assert response.status_code == status
        assert response.json() == {"error": error, "message": response.json()["message"], "path": response.request.url.path}
