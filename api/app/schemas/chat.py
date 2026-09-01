"""
Synkora API — Chat Schemas

Request/response models for the AI-powered code chat endpoint.
Supports context-aware Q&A over repository code using RAG
(Retrieval-Augmented Generation).
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in the chat conversation."""
    role: str = Field(
        ...,
        description="The role of the message author: 'user' or 'assistant'.",
        examples=["user", "assistant"],
    )
    content: str = Field(
        ...,
        min_length=1,
        description="The text content of the message.",
    )


class ChatRequest(BaseModel):
    """Request body for the code chat endpoint."""
    repository_id: str = Field(
        ...,
        description="ID of the repository to chat about.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's question about the codebase.",
        examples=["How does the authentication flow work?"],
    )
    history: List[ChatMessage] = Field(
        default_factory=list,
        max_length=20,
        description="Previous messages in the conversation for context continuity.",
    )
    include_code_context: bool = Field(
        default=True,
        description="Whether to search and include relevant code snippets as context.",
    )
    max_context_chunks: int = Field(
        default=5,
        ge=1,
        le=15,
        description="Max number of code chunks to include as RAG context.",
    )


class CodeContext(BaseModel):
    """A code snippet retrieved as context for the AI response."""
    file_path: str
    content_type: str
    content: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    relevance_score: float


class ChatResponse(BaseModel):
    """Response body from the code chat endpoint."""
    answer: str = Field(description="The AI-generated answer.")
    code_context: List[CodeContext] = Field(
        default_factory=list,
        description="Code snippets used as context for generating the answer.",
    )
    model: str = Field(description="The AI model used to generate the response.")
    tokens_used: Optional[int] = Field(
        default=None,
        description="Total tokens consumed (prompt + completion).",
    )
