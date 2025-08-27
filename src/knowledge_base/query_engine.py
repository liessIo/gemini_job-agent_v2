# src/knowledge_base/query_engine.py

from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Any, Dict, List, Optional
from chromadb.api.types import QueryResult # <-- IMPORT THE CORRECT TYPE

# ... (Pfade bleiben gleich) ...
BASE_DIR = Path(__file__).resolve().parent.parent.parent
VECTOR_STORE_PATH = BASE_DIR / "data" / "vector_stores"


def query_knowledge_base(query: str, model: Any, language: str = 'de', n_results: int = 3) -> Optional[QueryResult]: # <-- USE THE CORRECT TYPE HINT
    """
    Sucht in der Wissensbasis und gibt die Ergebnisse als ChromaDB QueryResult-Objekt zurück.
    """
    db_path = str(VECTOR_STORE_PATH / language)
    collection_name = f"jobs_{language}"

    try:
        persistent_client = chromadb.PersistentClient(path=db_path)
        collection = persistent_client.get_collection(name=collection_name)
    except ValueError:
        print(f"\n❌ Fehler: Die Sammlung '{collection_name}' wurde nicht gefunden.")
        return None

    query_embedding = model.encode(query).tolist()

    results: QueryResult = collection.query( # You can also add the type hint here for clarity
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results