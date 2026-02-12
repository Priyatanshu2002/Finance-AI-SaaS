"""
Documents API — List and manage user documents.
GET /api/documents
"""

import structlog
from fastapi import APIRouter

from models.schemas import DocumentListItem

logger = structlog.get_logger()
router = APIRouter()


@router.get("/documents", response_model=list[DocumentListItem])
async def list_documents(
    organization_id: str = "default",
    limit: int = 50,
    offset: int = 0,
):
    """
    List all documents for an organization.

    Returns metadata and processing status for each document.
    """
    # TODO: Query Supabase/PostgreSQL
    # For now, return empty list
    logger.info(
        "Documents listed",
        organization_id=organization_id,
        limit=limit,
        offset=offset,
    )

    return []
