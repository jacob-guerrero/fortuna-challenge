import logging
import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
POLICIES_DIR = BASE_DIR / "docs" / "politicas"
DB_DIR = BASE_DIR / "data" / "vectordb"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

def section_for(text: str) -> str:
    match = re.search(r"(?m)^\s*(\d+(?:\.\d+)*\.?\s+[^\n]+)", text)
    return match.group(1).strip() if match else "Introducción"


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size debe ser positivo y overlap menor que chunk_size.")
    normalized = " ".join(text.split())
    return [normalized[start : start + chunk_size] for start in range(0, len(normalized), chunk_size - overlap)]


def extract_pages(pdf_path: Path) -> list[str]:
    return [page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages]

def ingest_policies() -> int:
    """Indexa cada fragmento con su documento, página y sección de origen."""
    if not POLICIES_DIR.exists():
        raise FileNotFoundError(f"No existe el directorio de políticas: {POLICIES_DIR}")
    DB_DIR.mkdir(parents=True, exist_ok=True)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(name="politicas_fortuna")
    except ValueError:
        pass
    collection = client.create_collection(name="politicas_fortuna", embedding_function=sentence_transformer_ef)

    doc_ids = []
    documents = []
    metadatas = []

    for pdf_path in sorted(POLICIES_DIR.glob("*.pdf")):
        for page_number, page_text in enumerate(extract_pages(pdf_path), start=1):
            page_section = section_for(page_text)
            for chunk_number, chunk in enumerate(chunk_text(page_text)):
                if not chunk:
                    continue
                doc_ids.append(f"{pdf_path.stem}-p{page_number}-c{chunk_number}")
                documents.append(chunk)
                metadatas.append({"document": pdf_path.name, "page": page_number, "section": page_section})

    # Insertamos todo en ChromaDB de una vez
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=doc_ids
        )
        logger.info("Ingesta completada: %s fragmentos indexados.", len(documents))
        return len(documents)
    raise ValueError("No se extrajo contenido de los PDFs de políticas.")

if __name__ == "__main__":
    ingest_policies()
