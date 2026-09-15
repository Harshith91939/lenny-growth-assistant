import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .config import settings
from .db import SessionLocal
from .api import router

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
app=FastAPI(title="The Lenny Growth Assistant", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.cors_origins], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.get("/health")
async def health():
    db_ok=False
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
            db_ok=True
    except Exception:
        pass
    return {"status":"ok" if db_ok else "degraded","database":db_ok,"provider":settings.llm_provider}
