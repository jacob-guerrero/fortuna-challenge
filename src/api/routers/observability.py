from fastapi import APIRouter

from src.api.schemas.policy import TelemetryResponse
from src.core.telemetry import metrics_collector

router = APIRouter(prefix="/observabilidad", tags=["Observabilidad"])


@router.get("/resumen", response_model=TelemetryResponse)
def get_summary() -> TelemetryResponse:
    return TelemetryResponse(**metrics_collector.summary().__dict__)
