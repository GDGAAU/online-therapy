'''
ai/models.py
Django model for storing knowledge chunks with vector embeddings for RAG chatbot.



'''
from django.db import models
from pgvector.django import VectorField


class Document(models.Model):
    """
    Stores knowledge chunks for RAG chatbot
    """

    title = models.CharField(max_length=255)
    content = models.TextField()

    embedding = VectorField(dimensions=384)

    source = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


# ─────────────────────────────────────────────
# Chat Session (conversation container)
# ─────────────────────────────────────────────
class ChatSession(models.Model):
    user = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )
    created_at = models.DateTimeField(auto_now_add=True)


# ─────────────────────────────────────────────
# Chat Messages (history memory)
# ─────────────────────────────────────────────
class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)