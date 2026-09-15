from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import MessageModel
from .retrieval import retrieve
from .llm import generate
from .skills import (
    QA_SYSTEM,
    SHIP30_SKILL,
    ARTIFACT_SYSTEM,
)


async def session_context(
    db: AsyncSession,
    session_id,
    limit=8,
):
    result = await db.execute(
        select(MessageModel)
        .where(
            MessageModel.session_id == session_id
        )
        .order_by(
            MessageModel.created_at.desc()
        )
        .limit(limit)
    )

    rows = list(
        reversed(result.scalars().all())
    )

    return "\n".join(
        f"{message.role}: {message.content}"
        for message in rows
    )


def evidence_block(sources):
    if not sources:
        return "NO TRANSCRIPT EVIDENCE WAS FOUND."

    output = []

    for index, source in enumerate(
        sources,
        1,
    ):
        output.append(
            f"[SOURCE {index}] "
            f"{source['title']} — "
            f"{source.get('guest') or 'Unknown guest'}\n"
            f"URL: "
            f"{source.get('source_url') or 'Unknown'}\n"
            f"PASSAGE:\n"
            f"{source['content']}"
        )

    return "\n\n".join(output)


async def answer(
    db: AsyncSession,
    session_id,
    question: str,
    provider: str = "ollama",
):
    """
    Answer a user question using retrieved
    Lenny Podcast transcript evidence.

    provider:
        ollama     -> local Ollama
        anthropic  -> Claude Agent SDK
    """

    sources = await retrieve(
        db,
        question,
    )

    context = await session_context(
        db,
        session_id,
    )

    prompt = f"""
CONVERSATION:
{context}

RETRIEVED TRANSCRIPT EVIDENCE:
{evidence_block(sources)}

USER QUESTION:
{question}
"""

    response = await generate(
        prompt,
        QA_SYSTEM,
        provider=provider,
    )

    return response, sources


async def make_essay(
    db: AsyncSession,
    session_id,
    provider: str = "ollama",
):
    context = await session_context(
        db,
        session_id,
        limit=12,
    )

    query = (
        context[-5000:]
        if context
        else "product growth"
    )

    sources = await retrieve(
        db,
        query,
    )

    prompt = f"""
CURRENT CONVERSATION:
{context}

RETRIEVED TRANSCRIPT EVIDENCE:
{evidence_block(sources)}

TASK:
Transform the current discussion into an approximately
1,250-word Ship 30 for 30 style essay.

The essay must:
- have a compelling title
- open with a strong hook
- develop one clear central idea
- use narrative progression
- contain specific examples and insights from the evidence
- use short paragraphs and useful section headings
- avoid turning the essay into a numbered list
- end with a practical takeaway
- remain grounded in the supplied transcript evidence

Return ONLY the finished Markdown essay.
"""

    response = await generate(
        prompt,
        SHIP30_SKILL,
        provider=provider,
    )

    return response, sources


async def make_artifact(
    db: AsyncSession,
    session_id,
    request: str,
    provider: str = "ollama",
):
    context = await session_context(
        db,
        session_id,
        limit=12,
    )

    query = (
        context[-5000:]
        if context
        else request
    )

    sources = await retrieve(
        db,
        query,
    )

    prompt = f"""
CONVERSATION:
{context}

RETRIEVED TRANSCRIPT EVIDENCE:
{evidence_block(sources)}

ARTIFACT REQUEST:
{request}

IMPORTANT:
If the requested artifact is HTML, return ONLY the
complete HTML document.

Do NOT explain the result.
Do NOT use Markdown code fences.
Do NOT write ```html.
Do NOT add text before or after the HTML.
"""

    result = await generate(
        prompt,
        ARTIFACT_SYSTEM,
        provider=provider,
    )

    return result, sources