import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .models import SessionModel, MessageModel
from .agent import answer, make_essay, make_artifact
from .artifacts import sanitize_html


router = APIRouter(prefix="/api")

log = logging.getLogger("lenny")


class MessageIn(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=12000
    )

    provider: str = Field(
        default="ollama",
        pattern="^(ollama|anthropic)$"
    )


class ArtifactIn(BaseModel):
    request: str = Field(
        min_length=1,
        max_length=4000
    )

    type: str = Field(
        pattern="^(markdown|html)$"
    )

    provider: str = Field(
        default="ollama",
        pattern="^(ollama|anthropic)$"
    )


@router.post("/sessions")
async def create_session(
    db: AsyncSession = Depends(get_db)
):
    s = SessionModel(
        id=uuid.uuid4(),
        title="New Chat"
    )

    db.add(s)
    await db.commit()

    return {
        "id": str(s.id),
        "title": s.title
    }


@router.get("/sessions")
async def sessions(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SessionModel)
        .order_by(SessionModel.updated_at.desc())
    )

    return [
        {
            "id": str(s.id),
            "title": s.title
        }
        for s in result.scalars().all()
    ]


@router.get("/sessions/{session_id}/messages")
async def messages(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MessageModel)
        .where(
            MessageModel.session_id == session_id
        )
        .order_by(MessageModel.created_at)
    )

    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "metadata": m.metadata_
        }
        for m in result.scalars().all()
    ]


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: uuid.UUID,
    payload: MessageIn,
    db: AsyncSession = Depends(get_db)
):
    s = await db.get(
        SessionModel,
        session_id
    )

    if not s:
        raise HTTPException(
            404,
            "Session not found"
        )

    # Persist user message
    db.add(
        MessageModel(
            id=uuid.uuid4(),
            session_id=session_id,
            role="user",
            content=payload.content,
            metadata_={
                "provider": payload.provider
            }
        )
    )

    await db.commit()

    try:
        # Pass selected provider through
        # to the agent/LLM layer.
        response, sources = await answer(
            db,
            session_id,
            payload.content,
            provider=payload.provider
        )

    except Exception as e:
        log.exception(
            "message_failed"
        )

        raise HTTPException(
            503,
            f"AI service unavailable: {e}"
        )

    source_data = [
        {
            "title": x["title"],
            "guest": x.get("guest"),
            "url": x.get("source_url"),
            "content": x["content"][:500]
        }
        for x in sources
    ]

    # Persist assistant response
    db.add(
        MessageModel(
            id=uuid.uuid4(),
            session_id=session_id,
            role="assistant",
            content=response,
            metadata_={
                "sources": source_data,
                "provider": payload.provider
            }
        )
    )

    s.title = payload.content[:60]

    await db.commit()

    return {
        "content": response,
        "sources": source_data,
        "provider": payload.provider
    }


@router.post("/sessions/{session_id}/artifacts")
async def artifact(
    session_id: uuid.UUID,
    payload: ArtifactIn,
    db: AsyncSession = Depends(get_db)
):
    if not await db.get(
        SessionModel,
        session_id
    ):
        raise HTTPException(
            404,
            "Session not found"
        )

    try:
        result, sources = await make_artifact(
            db,
            session_id,
            payload.request,
            provider=payload.provider
        )

    except Exception as e:
        log.exception(
            "artifact_failed"
        )

        raise HTTPException(
            503,
            f"AI service unavailable: {e}"
        )

    if payload.type == "html":
        result = sanitize_html(result)

    return {
        "type": payload.type,
        "content": result,
        "sources": [
            {
                "title": x["title"],
                "url": x.get("source_url")
            }
            for x in sources
        ]
    }