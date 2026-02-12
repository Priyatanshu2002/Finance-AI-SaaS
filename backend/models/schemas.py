"""
Pydantic data models — matching gemini.md schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Enums ───────────────────────────────────────────────────────────────────

class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    IMAGE = "image"


class DocumentType(str, Enum):
    TEN_K = "10-K"
    TEN_Q = "10-Q"
    ANNUAL_REPORT = "annual_report"
    RENT_ROLL = "rent_roll"
    OFFERING_MEMO = "offering_memorandum"
    TERM_SHEET = "term_sheet"
    CONTRACT = "contract"
    FINANCIAL_STATEMENT = "financial_statement"
    OTHER = "other"


class AgentType(str, Enum):
    CLAUDE_SPECIALIST = "claude_specialist"       # Anthropic (Precision)
    GEMINI_ARCHIVIST = "gemini_archivist"         # Google (Volume/Context)
    DEEPSEEK_MATHEMATICIAN = "deepseek_math"      # DeepSeek (Reasoning)
    GPT_PROPHET = "gpt_prophet"                   # OpenAI (Predictive)


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


# ─── Input Models ────────────────────────────────────────────────────────────

class DocumentMetadata(BaseModel):
    company_name: Optional[str] = None
    fiscal_period: Optional[str] = None
    currency: Optional[str] = None
    language: str = "en"


class DocumentUpload(BaseModel):
    """Represents an uploaded document record in the database."""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    uploaded_by: str
    organization_id: str
    filename: str
    file_type: FileType
    file_size_bytes: int
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    document_type: Optional[DocumentType] = None
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    status: ProcessingStatus = ProcessingStatus.PENDING


# ─── Output Models ───────────────────────────────────────────────────────────

class SourceCoordinates(BaseModel):
    x: float
    y: float
    w: float
    h: float


class LineItem(BaseModel):
    label: str
    standardized_label: str
    values: dict[str, Optional[float]]
    currency: str = "USD"
    confidence: float = Field(ge=0, le=1)
    source_page: Optional[int] = None
    source_coordinates: Optional[SourceCoordinates] = None


class FinancialStatement(BaseModel):
    periods: list[str] = []
    line_items: list[LineItem] = []


class ValidationResults(BaseModel):
    balance_sheet_balanced: Optional[bool] = None
    cash_flow_reconciled: Optional[bool] = None
    cross_statement_consistent: Optional[bool] = None
    items_flagged_for_review: int = 0
    flags: list[str] = []


class ExtractionResult(BaseModel):
    """Complete extraction output — matches gemini.md output schema."""
    extraction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    document_type_detected: Optional[str] = None
    selected_agent: AgentType = AgentType.CLAUDE_SPECIALIST
    quality_score: float = Field(default=0, ge=0, le=100)
    statements: dict[str, FinancialStatement] = Field(default_factory=lambda: {
        "income_statement": FinancialStatement(),
        "balance_sheet": FinancialStatement(),
        "cash_flow_statement": FinancialStatement(),
    })
    calculated_metrics: dict[str, dict[str, Optional[float]]] = Field(default_factory=dict)
    validation: ValidationResults = Field(default_factory=ValidationResults)
    status: ProcessingStatus = ProcessingStatus.PENDING


# ─── API Response Models ─────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: ProcessingStatus
    message: str


class DocumentListItem(BaseModel):
    document_id: str
    filename: str
    file_type: FileType
    document_type: Optional[DocumentType] = None
    upload_timestamp: datetime
    status: ProcessingStatus
    quality_score: Optional[float] = None
