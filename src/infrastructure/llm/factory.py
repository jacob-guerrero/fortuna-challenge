import os

from dotenv import load_dotenv

from src.domain.llm_port import LLMPort
from src.infrastructure.llm.dummy_adapter import DummyLLMAdapter
from src.infrastructure.llm.openai_compatible_adapter import OpenAICompatibleAdapter

load_dotenv()


def build_llm_adapter() -> LLMPort:
    """Selecciona el proveedor desde configuración, sin acoplar la API a él."""
    provider = os.getenv("AI_PROVIDER", "dummy").lower()
    if provider == "dummy":
        return DummyLLMAdapter()
    if provider == "openai_compatible":
        return OpenAICompatibleAdapter(
            api_key=os.getenv("AI_API_KEY", ""),
            model=os.getenv("AI_MODEL_NAME", "gpt-4o-mini"),
            base_url=os.getenv("AI_API_BASE_URL", "https://api.openai.com/v1"),
        )
    raise ValueError(f"AI_PROVIDER no soportado: {provider}")
