from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from src.domain.policy_search_port import PolicyChunk, PolicySearchPort


class ChromaPolicyRepository(PolicySearchPort):
    """Adaptador Chroma para la colección local generada por la ingesta."""

    def __init__(self, database_path: Path, embedding_model: str) -> None:
        self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        client = chromadb.PersistentClient(path=str(database_path))
        self._collection = client.get_collection(
            name="politicas_fortuna", embedding_function=self._embedding_function
        )

    def search(self, question: str, limit: int) -> list[PolicyChunk]:
        result = self._collection.query(
            query_texts=[question],
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        chunks: list[PolicyChunk] = []
        for document, metadata, distance in zip(documents, metadatas, distances):
            chunks.append(
                PolicyChunk(
                    content=document,
                    document=metadata["document"],
                    page=int(metadata["page"]),
                    section=metadata["section"],
                    score=round(max(0.0, 1 - float(distance)), 4),
                )
            )
        return sorted(chunks, key=lambda chunk: chunk.score, reverse=True)
