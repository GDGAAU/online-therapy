''' ai/urls.py'''


from django.urls import path
from ai.api.views import (
    ChatAPIView,
    ChatSessionAPIView,
    ChatMessagesAPIView,
)

urlpatterns = [
    # Chat sessions
    path("chats/", ChatSessionAPIView.as_view()),

    # Chat messages
    path("chats/<int:session_id>/messages/", ChatMessagesAPIView.as_view()),

    # Send message
    path("chat/", ChatAPIView.as_view()),
]