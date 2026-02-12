
"""
Financial NER Tool — Stage 4 of Extraction Pipeline
Uses Anthropic Claude Opus 4.6 to identify financial line items, periods, and currency.
"""

import os
import json
import structlog
from typing import Any, Dict, List, Optional
from anthropic import Anthropic
from pydantic import BaseModel, Field

logger = structlog.get_logger()

# ─── Data Models ─────────────────────────────────────────────────────────────

class FinancialLineItem(BaseModel):
    label: str
    value: Optional[float]
    period: str
    currency: str
    confidence: float

class FinancialStatement(BaseModel):
    statement_type: str  # "Income Statement", "Balance Sheet", "Cash Flow"
    line_items: List[FinancialLineItem]

class ExtractionResult(BaseModel):
    document_type: str
    financial_data: List[FinancialStatement]
    agent_notes: str
    confidence: float

# ─── Prompts ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior financial analyst and accounting expert. Your task is to extract structured financial data from OCR text and tables.
You must identify:
1. The Document Type (e.g., 10-K, 10-Q, Annual Report).
2. The Period(s) covered (e.g., "FY2023", "Q1 2024").
3. The Currency (e.g., "USD", "EUR").
4. Line Items for Income Statement, Balance Sheet, and Cash Flow Statement.

Rules:
- VALIDITY: Only extract real numbers found in the text/tables. Do not calculate or hallucinate.
- LABELS: Use the exact label found in the document AND provide a standardized label if possible.
- STRUCTURE: Group items by statement type.
- CONFIDENCE: Assign a confidence score (0.0 - 1.0) based on extraction clarity.
- NULLS: If a value is missing, use null (None).
- SIGNS: Respect parentheses for negative numbers.
"""

USER_PROMPT_TEMPLATE = """
Here is the extracted text and table data from a financial document.

--- TEXT CONTENT ---
{text_content}

--- TABLE DATA ---
{table_content}

--- INSTRUCTIONS ---
Extract the financial data into the specified JSON format.
"""

# ─── Main Function ───────────────────────────────────────────────────────────

def analyze_financial_document(
    doc_text: str,
    table_data: Any,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes document text and tables using Claude Opus 4.6 to extract financial data.

    Args:
        doc_text: Raw text extracted from the document.
        table_data: Structured table data (list of dictionaries or objects).
        api_key: Anthropic API key. If None, looks for ANTHROPIC_API_KEY env var.

    Returns:
        Dict containing structured financial data (ExtractionResult).
    """
    
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key or key.startswith("dummy"):
        logger.warning("No valid Anthropic API key found. Returning mock data for development.")
        return _get_mock_response()

    client = Anthropic(api_key=key)
    
    # Prepare table content for prompt
    table_str = str(table_data) # Simple stringification for now, can be optimized
    
    prompt = USER_PROMPT_TEMPLATE.format(
        text_content=doc_text[:100000], # Truncate to avoid token limits if massive
        table_content=table_str[:50000]
    )

    try:
        logger.info("Sending request to Claude Opus 4.6 for Financial NER")
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            temperature=0.0,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response - assuming Claude returns JSON usage
        # In a real scenario we'd use tool_use or JSON mode
        response_text = message.content[0].text
        
        # Simple JSON extraction (robustness improvement needed for prod)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            return data
        else:
            logger.error("Failed to parse JSON from Claude response")
            return _get_mock_response(error="JSON Parse Error")

    except Exception as e:
        logger.error(f"Error calling Anthropic API: {str(e)}")
        return _get_mock_response(error=str(e))

def _get_mock_response(error: str = None) -> Dict[str, Any]:
    """Returns structured mock data when API is unavailable or fails."""
    return {
        "document_type": "10-K (Mock)",
        "financial_data": [
            {
                "statement_type": "Income Statement",
                "line_items": [
                    {"label": "Revenue", "value": 1000000, "period": "FY2023", "currency": "USD", "confidence": 0.95},
                    {"label": "Net Income", "value": 250000, "period": "FY2023", "currency": "USD", "confidence": 0.95}
                ]
            }
        ],
        "agent_notes": f"Mock data returned. {f'Error: {error}' if error else 'No API key provided.'}",
        "confidence": 0.0
    }

if __name__ == "__main__":
    # Test run
    print(analyze_financial_document("Test Doc", [], api_key="dummy"))
