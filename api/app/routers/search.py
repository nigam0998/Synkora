"""
Synkora API — Semantic Search Router

Provides natural-language code search powered by vector embeddings.
Accepts a free-text query, converts it to a vector, and retrieves the
most semantically similar code chunks from a repository.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.database import get_db
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.embedding_service import EmbeddingService

logger = get_logger("search_router")

router = APIRouter()


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Semantic Code Search",
    description=(
        "Search a repository's codebase using natural language. "
        "Returns the most semantically relevant functions, classes, "
        "and file chunks ranked by cosine similarity."
    ),
)
async def semantic_search(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Execute a semantic search against the stored code embeddings
    for a given repository.
    """
    logger.info(
        "semantic_search_request",
        query=body.query,
        repo_id=body.repository_id,
        limit=body.limit,
    )

    try:
        raw_results = await EmbeddingService.semantic_search(
            db=db,
            query=body.query,
            repository_id=body.repository_id,
            limit=body.limit,
            content_type=body.content_type,
            min_score=body.min_score,
        )
    except RuntimeError as e:
        # Raised when sentence-transformers is not installed
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        logger.error("semantic_search_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again later.",
        )

    results = [SearchResult(**r) for r in raw_results]

    return SearchResponse(
        query=body.query,
        repository_id=body.repository_id,
        total_results=len(results),
        results=results,
    )


@router.get(
    "/search/status/{repository_id}",
    summary="Embedding Index Status",
    description="Check whether embeddings have been generated for a repository.",
)
async def embedding_status(
    repository_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return the number of indexed code chunks for a repository."""
    from sqlalchemy import func, select
    from app.models.embedding import CodeEmbedding

    result = await db.execute(
        select(func.count(CodeEmbedding.id)).where(
            CodeEmbedding.repository_id == repository_id
        )
    )
    count = result.scalar() or 0

    return {
        "repository_id": repository_id,
        "indexed_chunks": count,
        "is_indexed": count > 0,
    }
