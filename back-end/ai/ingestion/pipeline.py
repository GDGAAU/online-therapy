

''' ai/ingestion/pipeline.py
===========================
Document ingestion pipeline for AI app. This module defines the full pipeline for processing and storing documents in the vector database.
'''



from ai.models import Document
from ai.services.embeddings import get_embedding
from ai.ingestion.chunking import chunk_text


def ingest_document(title: str, text: str, source: str = None):
    """
    Full ingestion pipeline:
    text → chunks → embeddings → pgvector storage
    """

    chunks = chunk_text(text)

    documents = []

    for chunk in chunks:
        embedding = get_embedding(chunk)

        doc = Document.objects.create(
            title=title,
            content=chunk,
            embedding=embedding,
            source=source
        )

        documents.append(doc)

    return documents