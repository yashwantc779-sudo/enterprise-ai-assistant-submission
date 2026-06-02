from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.logging import setup_logging
from app.db.database import init_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging()
    await init_database()
    yield


app = FastAPI(
    title="Enterprise AI Data Assistant",
    description="NLP-to-SQL platform with schema retrieval, SQL guardrails, and business-friendly responses.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["Data Assistant"])


@app.get("/")
async def root():
    return {
        "service": "Enterprise AI Data Assistant",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
