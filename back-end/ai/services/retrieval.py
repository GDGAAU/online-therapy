''' ai/services/retrieval.py'''


from pgvector.django import CosineDistance
from ai.models import Document
from ai.services.embeddings import get_embedding


def retrieve_similar_documents(query: str, top_k: int = 3):
    """
    Retrieve most relevant documents using vector similarity
    """

    query_embedding = get_embedding(query)

    results = (
        Document.objects.annotate(
            distance=CosineDistance("embedding", query_embedding)
        )
        .order_by("distance")[:top_k]
    )

    return [doc.content for doc in results]