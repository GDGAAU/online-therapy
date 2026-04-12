''' ai/serializers.py 
===========================
Serializers for AI app models and API endpoints.
This module defines serializers for:
- ChatSession: Represents a chat session with an ID and creation timestamp.
- ChatMessage: Represents a message in a chat session, including role, content, and timestamp.
- ChatRequestSerializer: For validating incoming chat messages with session ID.
- ChatResponseSerializer: For structuring outgoing chat responses with session ID and response content.

'''



from rest_framework import serializers
from ai.models import ChatSession, ChatMessage


# ─────────────────────────────
# Chat Session
# ─────────────────────────────
class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ["id", "created_at"]


# ─────────────────────────────
# Chat Message
# ─────────────────────────────
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["role", "message", "created_at"]


# ─────────────────────────────
# Send Message
# ─────────────────────────────
class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    session_id = serializers.IntegerField()


class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    response = serializers.CharField()