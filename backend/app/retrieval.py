from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .llm import embed, LLMError

async def retrieve(db: AsyncSession, query: str, limit: int = 5):
    vector = await embed(query)
    vector_sql = "[" + ",".join(str(x) for x in vector) + "]"
    stmt = text("""
        SELECT c.id, c.content, c.metadata, d.title, d.guest, d.source_url
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE c.embedding IS NOT NULL
        ORDER BY c.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)
    result = await db.execute(stmt, {"embedding": vector_sql, "limit": limit})
    rows = result.mappings().all()
    return [dict(r) for r in rows]
