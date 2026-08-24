import os
from functools import lru_cache
from pathlib import Path

from src.domain.policy_search_port import PolicySearchPort
from src.infrastructure.rag.chroma_policy_repository import ChromaPolicyRepository


@lru_cache(maxsize=1)
def build_policy_search_repository() -> PolicySearchPort:
    root = Path(__file__).resolve().parents[3]
    return ChromaPolicyRepository(
        database_path=root / "data" / "vectordb",
        embedding_model=os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    )
