''' ai/ingestion/chunking.py
===========================
Text chunking utility for AI document ingestion. This module defines a simple text splitter that breaks large documents into smaller chunks with optional overlap for better context retention in RAG pipelines.
'''


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    """
    Simple text splitter for RAG
    """

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # overlap for context continuity

    return chunks