import logging

from fastapi import APIRouter, Depends

from src.api.schemas.policy import PolicyQueryRequest, PolicyQueryResponse, PolicySourceResponse
from src.infrastructure.rag.factory import build_policy_search_repository
from src.use_cases.consultar_politica import ConsultarPoliticaUseCase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/politicas", tags=["Políticas"])


def get_policy_query_use_case() -> ConsultarPoliticaUseCase:
    return ConsultarPoliticaUseCase(build_policy_search_repository())


@router.post("/consultas", response_model=PolicyQueryResponse)
def consultar_politica(
    query: PolicyQueryRequest,
    use_case: ConsultarPoliticaUseCase = Depends(get_policy_query_use_case),
) -> PolicyQueryResponse:
    result = use_case.execute(query.question)
    logger.info(
        "Consulta RAG completada",
        extra={"event": "rag_query", "latency_ms": result.latency_ms, "abstained": result.abstained},
    )
    return PolicyQueryResponse(
        answer=result.answer,
        abstained=result.abstained,
        latency_ms=result.latency_ms,
        sources=[
            PolicySourceResponse(
                document=source.document, page=source.page, section=source.section, score=source.score
            )
            for source in result.sources
        ],
    )
