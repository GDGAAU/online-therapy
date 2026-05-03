"""ai/services/embeddings.py
===========================
Lightweight text embedding service for the AI app.

We avoid heavyweight ML dependencies (torch/nvidia) by using a deterministic,
hash-based embedding. It produces a fixed-size vector suitable for similarity
search in pgvector while staying fast and dependency-free.
"""

from __future__ import annotations

import hashlib
import struct


EMBEDDING_DIM = 384


def _hash_to_floats(seed: bytes, count: int) -> list[float]:
    floats: list[float] = []
    counter = 0

    while len(floats) < count:
        digest = hashlib.blake2b(seed + counter.to_bytes(4, "big"), digest_size=32).digest()
        for offset in range(0, len(digest), 4):
            if len(floats) >= count:
                break
            value = struct.unpack(">I", digest[offset:offset + 4])[0]
            floats.append((value / 2**32) * 2 - 1)
        counter += 1

    return floats


def get_embedding(text: str) -> list[float] | None:
    """Convert text → vector (384-dim)."""
    if not text:
        return None

    normalized = text.strip().lower().encode("utf-8")
    seed = hashlib.sha256(normalized).digest()
    return _hash_to_floats(seed, EMBEDDING_DIM)
