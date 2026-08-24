from src.domain.policy_search_port import PolicyChunk, PolicySearchPort
from src.use_cases.consultar_politica import ABSTENTION_MESSAGE, ConsultarPoliticaUseCase


class FakePolicyRepository(PolicySearchPort):
    def __init__(self, chunks: list[PolicyChunk]) -> None:
        self.chunks = chunks

    def search(self, question: str, limit: int) -> list[PolicyChunk]:
        return self.chunks[:limit]


def test_responde_con_citas_cuando_existe_evidencia():
    repository = FakePolicyRepository(
        [
            PolicyChunk(
                content="Las vacaciones se solicitan con quince días de anticipación.",
                document="POL-GTH-01_Vacaciones.pdf",
                page=2,
                section="3. Solicitud de vacaciones",
                score=0.81,
            )
        ]
    )

    result = ConsultarPoliticaUseCase(repository).execute("¿Con cuánto tiempo solicito vacaciones?")

    assert not result.abstained
    assert "POL-GTH-01_Vacaciones.pdf" in result.answer
    assert "pág. 2" in result.answer
    assert result.sources[0].section == "3. Solicitud de vacaciones"


def test_se_abstiene_sin_evidencia_suficiente():
    repository = FakePolicyRepository(
        [PolicyChunk("Texto irrelevante", "POL-ADM-04_Viaticos.pdf", 1, "Introducción", 0.12)]
    )

    result = ConsultarPoliticaUseCase(repository).execute("¿Cuál es el menú de la cafetería?")

    assert result.abstained
    assert result.answer == ABSTENTION_MESSAGE
    assert result.sources == []
