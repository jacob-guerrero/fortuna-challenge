import json
import logging

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

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
                    "content": "Clasifica tickets. Responde solo JSON con categoria y prioridad.",
                },
                {"role": "user", "content": texto},
            ],
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        result = json.loads(content)
        if not {"categoria", "prioridad"}.issubset(result):
            raise ValueError("El proveedor de IA devolvió una clasificación incompleta.")
        return result
