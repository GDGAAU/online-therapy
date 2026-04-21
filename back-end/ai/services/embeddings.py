''' ai/services/embeddings.py
===========================
Text embedding service for AI app. This module defines the function to convert text into vector embeddings using a lightweight local model (SentenceTransformer). 
The resulting vectors are stored in the database and used for similarity search in RAG pipelines.
'''

from sentence_transformers import SentenceTransformer

# lightweight local embedding model
_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str):
    """
    Convert text → vector (384-dim)
    """
    if not text:
        return None

    return _model.encode(text).tolist()