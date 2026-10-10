"""Indexation et recherche sémantique des passages de CV."""
import math
import os

from litellm import embedding

from core.chunking import chunk_markdown

DEFAULT_TOP_K = 8


def candidate_name(profile: dict | None, fallback: str) -> str:
    if not isinstance(profile, dict):
        return fallback
    full = f"{profile.get('firstName') or ''} {profile.get('lastName') or ''}".strip()
    return full or fallback


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Calcule un vecteur par texte avec le modèle d'embeddings configuré."""
    if not texts:
        return []
    model = os.getenv("EMBEDDING_MODEL", "gemini/text-embedding-004")
    response = embedding(model=model, input=texts)
    data = response.data if hasattr(response, "data") else response["data"]
    vectors = []
    for item in data:
        if isinstance(item, dict):
            vectors.append(item["embedding"])
        else:
            vectors.append(item.embedding)
    if len(vectors) != len(texts):
        raise RuntimeError("Le modèle d'embeddings n'a pas renvoyé un vecteur par passage.")
    return vectors


def upsert_document(chunks: list[dict], filename: str, markdown: str, profile: dict | None) -> list[dict]:
    """Remplace les passages déjà indexés pour ce fichier."""
    kept = [chunk for chunk in chunks if chunk.get("filename") != filename]
    pieces = chunk_markdown(markdown)
    if not pieces:
        return kept
    vectors = embed_texts([piece["text"] for piece in pieces])
    name = candidate_name(profile, filename)
    for piece, vector in zip(pieces, vectors):
        kept.append(
            {
                "filename": filename,
                "candidate": name,
                "section": piece["section"],
                "text": piece["text"],
                "embedding": vector,
            }
        )
    return kept


def search_chunks(query: str, chunks: list[dict], k: int = DEFAULT_TOP_K) -> list[dict]:
    """Retourne les passages les plus proches de la requête, sans leur vecteur."""
    query = (query or "").strip()
    if not query or not chunks:
        return []
    query_vector = embed_texts([query])[0]
    scored = [(_cosine(query_vector, chunk["embedding"]), chunk) for chunk in chunks]
    scored.sort(key=lambda item: item[0], reverse=True)
    results = []
    for score, chunk in scored[:k]:
        results.append(
            {
                "filename": chunk["filename"],
                "candidate": chunk["candidate"],
                "section": chunk["section"],
                "text": chunk["text"],
                "score": round(score, 3),
            }
        )
    return results


def _cosine(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    norm_left = math.sqrt(sum(a * a for a in left))
    norm_right = math.sqrt(sum(b * b for b in right))
    if norm_left == 0 or norm_right == 0:
        return 0.0
    return dot / (norm_left * norm_right)
