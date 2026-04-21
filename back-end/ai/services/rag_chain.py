

''' ai/services/rag_chain.py
===========================
RAG chain implementation for AI app. This module defines the main pipeline for generating AI responses using Retrieval-Augmented Generation (RAG).
 The pipeline includes retrieving relevant documents based on the user query, formatting the prompt with retrieved context, and generating a response using the Groq API. 
 This allows the AI assistant to provide informed answers based on the ingested knowledge base. we use langchain's ChatPromptTemplate for flexible prompt formatting and Groq for efficient LLM inference.
'''


import os
from groq import Groq

from langchain_core.prompts import ChatPromptTemplate
from ai.services.retrieval import retrieve_similar_documents

# Groq client
client = Groq(api_key=os.environ.get("GROK_API_KEY"))


# Prompt template
prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant for an online therapy platform.

Use ONLY the context below to answer the question.
If the answer is not in the context, say "I don't know based on the provided context but I can help you with other questions".

Context:
{context}

Question:
{question}

Answer clearly and professionally:
""")


def generate_answer(question: str):
    """
    Full RAG pipeline:
    retrieval → prompt → Groq → answer
    """

    
    docs = retrieve_similar_documents(question)

    context = "\n\n".join(docs)

   
    formatted_prompt = prompt.format(
        context=context,
        question=question
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": formatted_prompt}
        ]
    )

    return response.choices[0].message.content