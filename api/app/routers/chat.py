"""
Synkora API — Chat Router

AI-powered contextual Q&A over repository code.
Uses Retrieval-Augmented Generation (RAG) — retrieves semantically
relevant code chunks via pgvector, then feeds them as context to the
LLM for grounded, accurate answers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CodeContext,
)
from app.services.embedding_service import EmbeddingService

logger = get_logger("chat_router")

router = APIRouter()

# ── System Prompt ────────────────────────────────────────────────────────

CHAT_SYSTEM_PROMPT = """\
You are Synkora AI, an expert code assistant embedded in a repository analysis platform.

You answer questions about a codebase using the provided code context snippets.
Your responses must be:
- Accurate and grounded in the provided code context
- Clear and well-structured with markdown formatting
- Helpful for developers trying to understand or improve the codebase
- Concise — avoid repeating the entire code snippet back unless necessary

If the code context does not contain enough information to answer the question,
say so honestly rather than speculating. Suggest what the developer could look
for instead.
"""


def _build_context_block(chunks: list[dict]) -> str:
    """Format retrieved code chunks into a markdown context block for the LLM."""
    if not chunks:
        return "_No relevant code found in the repository index._"

    blocks = []
    for i, chunk in enumerate(chunks, 1):
        header = f"### Chunk {i}: `{chunk['file_path']}` ({chunk['content_type']})"
        if chunk.get("line_start") and chunk.get("line_end"):
            header += f" — Lines {chunk['line_start']}–{chunk['line_end']}"
        header += f"  (relevance: {chunk['score']:.0%})"

        blocks.append(f"{header}\n```\n{chunk['content']}\n```")

    return "\n\n".join(blocks)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Code Chat (RAG)",
    description=(
        "Ask a natural-language question about a repository's codebase. "
        "The system retrieves relevant code snippets via semantic search, "
        "then uses an LLM to generate a grounded answer."
    ),
)
async def code_chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """RAG-powered code Q&A endpoint."""

    if not settings.AI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are not configured. Set AI_API_KEY in .env.",
        )

    logger.info(
        "chat_request",
        repo_id=body.repository_id,
        message_len=len(body.message),
        history_len=len(body.history),
    )

    # ── 1. Retrieve relevant code context ────────────────────────────
    code_chunks: list[dict] = []
    if body.include_code_context:
        try:
            code_chunks = await EmbeddingService.semantic_search(
                db=db,
                query=body.message,
                repository_id=body.repository_id,
                limit=body.max_context_chunks,
                min_score=0.25,
            )
        except Exception as e:
            logger.warning("chat_context_retrieval_failed", error=str(e))
            # Continue without context — the LLM can still try to help

    context_block = _build_context_block(code_chunks)

    # ── 2. Build conversation messages ───────────────────────────────
    messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
    ]

    # Inject code context as a system-level reference
    messages.append({
        "role": "system",
        "content": f"## Retrieved Code Context\n\n{context_block}",
    })

    # Add conversation history
    for msg in body.history:
        messages.append({"role": msg.role, "content": msg.content})

    # Add the current user message
    messages.append({"role": "user", "content": body.message})

    # ── 3. Call the LLM ──────────────────────────────────────────────
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
        )

        response = await client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )

        answer = response.choices[0].message.content or ""
        tokens = (
            response.usage.total_tokens if response.usage else None
        )

        logger.info(
            "chat_response_generated",
            answer_len=len(answer),
            tokens=tokens,
        )

    except Exception as e:
        logger.error("chat_llm_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {e}",
        )

    # ── 4. Build response ────────────────────────────────────────────
    return ChatResponse(
        answer=answer.strip(),
        code_context=[
            CodeContext(
                file_path=c["file_path"],
                content_type=c["content_type"],
                content=c["content"],
                line_start=c.get("line_start"),
                line_end=c.get("line_end"),
                relevance_score=c["score"],
            )
            for c in code_chunks
        ],
        model=settings.AI_MODEL,
        tokens_used=tokens,
    )
