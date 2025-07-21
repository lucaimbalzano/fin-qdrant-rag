from openai import OpenAI
from typing import List, Optional


def get_embeddings(
    texts: List[str],
    model: str = "text-embedding-3-small",
    api_key: Optional[str] = None,
    batch_size: int = 16
) -> List[List[float]]:
    """
    Get embeddings for a list of texts using OpenAI's Embedding API (v1.x+).
    Args:
        texts: List of input strings.
        model: OpenAI embedding model name.
        api_key: Optional API key (if not set in env).
        batch_size: Number of texts per API call.
    Returns:
        List of embedding vectors (one per input text).
    """
    client = OpenAI(api_key=api_key)
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        response = client.embeddings.create(input=batch, model=model)
        batch_embeddings = [d.embedding for d in response.data]
        embeddings.extend(batch_embeddings)
    return embeddings
