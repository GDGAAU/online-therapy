
''' ai/services/chat_service.py
===========================
Chat service for AI app. This module defines the main pipeline for handling chat interactions, 
including saving messages, building conversation history, and generating AI responses using the RAG chain.

'''


from ai.models import ChatSession, ChatMessage
from ai.services.rag_chain import generate_answer


# ─────────────────────────────
# Save message
# ─────────────────────────────
def save_message(session, role, message):
    return ChatMessage.objects.create(
        session=session,
        role=role,
        message=message
    )


# ─────────────────────────────
# Build history
# ─────────────────────────────
def build_history(session, limit=10):
    messages = session.messages.order_by("-created_at")[:limit]
    messages = reversed(messages)

    history = ""
    for msg in messages:
        history += f"{msg.role}: {msg.message}\n"

    return history


# ─────────────────────────────
# MAIN CHAT PIPELINE
# ─────────────────────────────
def chat_pipeline(user, session_id, message):
    try:
        session = ChatSession.objects.get(id=session_id, user=user)
    except ChatSession.DoesNotExist:
        raise Exception("Session not found")
    save_message(session, "user", message)
    history = build_history(session)

    full_input = f"""
Conversation history:
{history}

User question:
{message}
"""

    response = generate_answer(full_input)

    save_message(session, "assistant", response)

    return response