from pydantic import BaseModel, Field


class PolicyQueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)


class PolicySourceResponse(BaseModel):
    document: str
    page: int
    section: str
    score: float


class PolicyQueryResponse(BaseModel):
    answer: str
    abstained: bool
    latency_ms: float
    sources: list[PolicySourceResponse]


class TelemetryResponse(BaseModel):
    requests: int
    total_latency_ms: float
    llm_calls: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_usd: float
