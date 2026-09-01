"""
Synkora API — Embedding Service

Generates vector embeddings for source code chunks using a local SentenceTransformer model.
Stores the resulting vectors into the database using pgvector.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.core.logging import get_logger
from app.models.embedding import CodeEmbedding
from app.schemas.ast import ParsedFile

logger = get_logger("embedding_service")


class EmbeddingService:
    """Service for generating and storing semantic code embeddings."""

    _model = None

    @classmethod
    def _get_model(cls):
        """Lazily load the sentence-transformers model to save memory until needed."""
        if cls._model is None:
            logger.info("loading_embedding_model", model_name="all-MiniLM-L6-v2")
            try:
                from sentence_transformers import SentenceTransformer
                # Use a small, fast model suitable for code and text
                cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                logger.error("sentence_transformers_not_installed")
                raise RuntimeError("sentence-transformers package is required for embeddings.")
        return cls._model

    @classmethod
    def generate_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of text strings."""
        if not texts:
            return []
        
        model = cls._get_model()
        # encode() returns a numpy array, we convert to list of floats for pgvector
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @classmethod
    async def process_parsed_file(
        cls, 
        db: AsyncSession, 
        repo_id: str, 
        analysis_id: str, 
        parsed_file: ParsedFile, 
        base_path: Path
    ) -> int:
        """
        Extract code chunks from a ParsedFile, generate embeddings, and store them.
        Returns the number of embeddings created.
        """
        file_abs_path = base_path / parsed_file.filepath
        if not file_abs_path.exists():
            return 0

        try:
            source_lines = file_abs_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            return 0

        chunks: List[Dict[str, Any]] = []

        def extract_chunk(start_line: int, end_line: int) -> str:
            # Lines are 1-indexed in AST
            start_idx = max(0, start_line - 1)
            end_idx = min(len(source_lines), end_line)
            return "\n".join(source_lines[start_idx:end_idx])

        # 1. Chunk Classes
        for cls_def in parsed_file.classes:
            content = extract_chunk(cls_def.start_line, cls_def.end_line)
            if content.strip():
                chunks.append({
                    "content_type": "class",
                    "content": content,
                    "line_start": cls_def.start_line,
                    "line_end": cls_def.end_line
                })

        # 2. Chunk Functions
        for func_def in parsed_file.functions:
            content = extract_chunk(func_def.start_line, func_def.end_line)
            if content.strip():
                chunks.append({
                    "content_type": "function",
                    "content": content,
                    "line_start": func_def.start_line,
                    "line_end": func_def.end_line
                })
        
        # 3. If no classes or functions (e.g. simple script), chunk the whole file
        if not parsed_file.classes and not parsed_file.functions:
            content = "\n".join(source_lines)
            if content.strip():
                chunks.append({
                    "content_type": "file",
                    "content": content,
                    "line_start": 1,
                    "line_end": len(source_lines)
                })

        if not chunks:
            return 0

        # Generate embeddings in one batch
        texts_to_embed = [chunk["content"] for chunk in chunks]
        
        # Run CPU-bound generation in a thread pool to avoid blocking async loop
        loop = asyncio.get_running_loop()
        vectors = await loop.run_in_executor(None, cls.generate_embeddings, texts_to_embed)

        # Prepare DB records
        records = []
        for chunk, vector in zip(chunks, vectors):
            records.append({
                "repository_id": repo_id,
                "analysis_id": analysis_id,
                "file_path": parsed_file.filepath,
                "content_type": chunk["content_type"],
                "content": chunk["content"],
                "line_start": chunk["line_start"],
                "line_end": chunk["line_end"],
                "embedding": vector
            })

        # Insert records
        if records:
            stmt = insert(CodeEmbedding).values(records)
            await db.execute(stmt)
            await db.commit()

        return len(records)

    @classmethod
    async def semantic_search(
        cls,
        db: AsyncSession,
        query: str,
        repository_id: str,
        limit: int = 10,
        content_type: str | None = None,
        min_score: float = 0.3,
    ) -> list[dict]:
        """
        Search code embeddings by semantic similarity.

        Uses pgvector's cosine distance operator (`<=>`) to find the most
        relevant code chunks for a natural-language query.

        Returns a list of dicts with keys: file_path, content_type, content,
        line_start, line_end, score.
        """
        from sqlalchemy import text as sql_text

        # Generate query embedding
        loop = asyncio.get_running_loop()
        query_vectors = await loop.run_in_executor(
            None, cls.generate_embeddings, [query]
        )
        if not query_vectors:
            return []

        query_vector = query_vectors[0]
        vector_str = "[" + ",".join(str(v) for v in query_vector) + "]"

        # Build the SQL query
        # pgvector `<=>` returns cosine *distance* (0 = identical).
        # We convert to similarity: 1 - distance.
        sql = """
            SELECT
                file_path,
                content_type,
                content,
                line_start,
                line_end,
                1 - (embedding <=> :query_vec) AS score
            FROM code_embeddings
            WHERE repository_id = :repo_id
        """
        params: dict = {
            "query_vec": vector_str,
            "repo_id": repository_id,
        }

        if content_type:
            sql += " AND content_type = :ctype"
            params["ctype"] = content_type

        sql += """
            HAVING 1 - (embedding <=> :query_vec2) >= :min_score
            ORDER BY score DESC
            LIMIT :lim
        """
        # pgvector needs the vector reference again for HAVING
        params["query_vec2"] = vector_str
        params["min_score"] = min_score
        params["lim"] = limit

        # Wrap in a subquery to allow HAVING on alias
        wrapped_sql = f"""
            SELECT * FROM (
                SELECT
                    file_path,
                    content_type,
                    content,
                    line_start,
                    line_end,
                    1 - (embedding <=> :query_vec::vector) AS score
                FROM code_embeddings
                WHERE repository_id = :repo_id
                {"AND content_type = :ctype" if content_type else ""}
                ORDER BY embedding <=> :query_vec::vector
                LIMIT :lim
            ) sub
            WHERE score >= :min_score
            ORDER BY score DESC
        """
        params_clean = {
            "query_vec": vector_str,
            "repo_id": repository_id,
            "min_score": min_score,
            "lim": limit,
        }
        if content_type:
            params_clean["ctype"] = content_type

        result = await db.execute(sql_text(wrapped_sql), params_clean)
        rows = result.fetchall()

        return [
            {
                "file_path": row.file_path,
                "content_type": row.content_type,
                "content": row.content,
                "line_start": row.line_start,
                "line_end": row.line_end,
                "score": round(float(row.score), 4),
            }
            for row in rows
        ]
