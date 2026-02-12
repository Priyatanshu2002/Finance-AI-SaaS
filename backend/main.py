"""
Finance AI SaaS — Backend API
FastAPI service for financial document extraction and analysis.
"""

import os
import uuid
from contextlib import asynccontextmanager

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.upload import router as upload_router
from api.extract import router as extract_router
from api.documents import router as documents_router

load_dotenv()

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Starting Finance AI SaaS Backend")
    yield
    logger.info("Shutting down Finance AI SaaS Backend")


app = FastAPI(
    title="Finance AI SaaS API",
    description="AI-powered financial document extraction and analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(extract_router, prefix="/api", tags=["extraction"])
app.include_router(documents_router, prefix="/api", tags=["documents"])


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "service": "finance-ai-backend",
        "version": "0.1.0",
    }
