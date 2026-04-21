''' ai/api/views.py
===========================
API views for AI app. This module defines endpoints for:
1. ChatSessionAPIView: List and create chat sessions.
2. ChatMessagesAPIView: Get messages for a specific chat session.
3. ChatAPIView: Send a message to a chat session and get AI response.

'''


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from ai.models import ChatSession
from ai.api.serializers import (
    ChatResponseSerializer,
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatRequestSerializer,   
)
from ai.services.chat_service import chat_pipeline


# ─────────────────────────────
# 1. List + Create Chats
# ─────────────────────────────
class ChatSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all chat sessions for the authenticated user",
        responses=ChatSessionSerializer(many=True)
    )
    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user).order_by("-created_at")
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a new chat session",
        request=None,
        responses=ChatSessionSerializer
    )
    def post(self, request):
        session = ChatSession.objects.create(user=request.user)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)


# ─────────────────────────────
# 2. Get Messages of a Chat
# ─────────────────────────────
class ChatMessagesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get all messages for a chat session",
        parameters=[
            OpenApiParameter(
                name="session_id",
                description="Chat session ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            )
        ],
        responses=ChatMessageSerializer(many=True)
    )
    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        messages = session.messages.order_by("created_at")
        serializer = ChatMessageSerializer(messages, many=True)

        return Response(serializer.data)


# ─────────────────────────────
# 3. Send Message
# ─────────────────────────────
class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Send a message to the chat session",
        request=ChatRequestSerializer,   
        responses=ChatResponseSerializer
    )
    def post(self, request):
        message = request.data.get("message")
        session_id = request.data.get("session_id")

        if not message or not session_id:
            return Response(
                {"error": "message and session_id required"},
                status=400
            )

        try:
            response = chat_pipeline(request.user, session_id, message)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "session_id": session_id,
            "response": response
        })