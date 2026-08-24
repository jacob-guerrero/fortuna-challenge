import json
import logging
from time import perf_counter

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from src.core.telemetry import metrics_collector
from src.domain.llm_port import LLMPort

logger = logging.getLogger(__name__)


def _is_transient_provider_error(error: BaseException) -> bool:
    if isinstance(error, (httpx.TimeoutException, httpx.NetworkError)):
        return True
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code == 429 or error.response.status_code >= 500
    return False


class OpenAICompatibleAdapter(LLMPort):
    """Adaptador para proveedores compatibles con el endpoint Chat Completions."""

    def __init__(self, api_key: str, model: str, base_url: str, timeout_seconds: float = 5.0):
        if not api_key:
            raise ValueError("Falta AI_API_KEY para el proveedor de IA configurado.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception(_is_transient_provider_error),
        reraise=True,
    )
    def clasificar_ticket(self, texto: str) -> dict:
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente de TI experto que procesa tickets usando RAG.\n"
                        "Debes responder en formato JSON estrictamente con 4 claves:\n"
                        "- 'categoria': (Ej. Accesos, Hardware)\n"
                        "- 'prioridad': (Ej. Baja, Media, Alta, Crítica)\n"
                        "- 'respuesta_usuario': Tu respuesta para el empleado, basándote ÚNICAMENTE en las POLÍTICAS ENCONTRADAS (RAG) que acompañan al texto del usuario. "
                        "ATENCIÓN: Si la política proporcionada tiene Estado: Obsoleta, o si no hay información relevante, DEBES ABSTENERTE de inventar y responder EXACTAMENTE: 'No encontré información vigente para esto'.\n"
                        "- 'resumen_tecnico': Resumen de 1 línea estrictamente técnico para el área de TI (Ej: 'Usuario reporta HTTP 401')."
                    ),
                },
                {"role": "user", "content": texto},
            ],
        }

        start_time = perf_counter()

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=self.timeout,
        )

        latency_ms = round((perf_counter() - start_time) * 1000, 2)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Telemetría de tokens y coste estimado
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        # Costo gpt-4o-mini aproximado: $0.150 / 1M input, $0.600 / 1M output
        cost_usd = (prompt_tokens / 1_000_000 * 0.150) + (completion_tokens / 1_000_000 * 0.600)

        logger.info(
            "Telemetría LLM Registrada",
            extra={
                "event": "llm_telemetry",
                "latency_ms": latency_ms,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": cost_usd,
                "model": self.model
            }
        )
        metrics_collector.record_llm_call(prompt_tokens, completion_tokens, cost_usd)

        result = json.loads(content)
        if not {"categoria", "prioridad", "respuesta_usuario", "resumen_tecnico"}.issubset(result):
            raise ValueError("El proveedor de IA devolvió una respuesta incompleta.")
        return result
