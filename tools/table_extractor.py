"""
Table Extractor — Stage 3 of Extraction Pipeline
Detects and extracts tables from PDF documents.

Strategy:
1. Camelot lattice mode (bordered tables)
2. Camelot stream mode (borderless tables)
3. Tabula fallback
4. Clean numeric values (remove $, commas, handle parentheses as negative)
"""

import os
import re
from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger()


@dataclass
class ExtractedTable:
    """A single table extracted from a document."""
    table_id: int
    page_number: int
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    numeric_rows: list[list[float | None]] = field(default_factory=list)
    accuracy: float = 0.0
    method: str = "camelot_lattice"
    coordinates: dict = field(default_factory=dict)


@dataclass
class TableExtractionResult:
    """All tables extracted from a document."""
    file_path: str
    tables: list[ExtractedTable] = field(default_factory=list)
    total_tables: int = 0
    errors: list[str] = field(default_factory=list)


def clean_numeric(value: str) -> float | None:
    """
    Clean a financial numeric string to a float.

    Handles:
    - Currency symbols: $1,234.56 → 1234.56
    - Parentheses as negative: (1,234) → -1234.0
    - Dashes as zero: - → 0.0
    - Percentages: 12.5% → 12.5
    - Thousands: 1,234,567 → 1234567.0
    - Empty/whitespace → None
    """
    if not value or not value.strip():
        return None

    text = value.strip()

    # Handle dash as zero
    if text in ("-", "—", "–", "−"):
        return 0.0

    # Handle N/A, n/a, etc.
    if text.lower() in ("n/a", "na", "nm", "n/m", "nil"):
        return None

    # Detect negative (parentheses)
    is_negative = False
    if text.startswith("(") and text.endswith(")"):
        is_negative = True
        text = text[1:-1]

    # Remove currency symbols and whitespace
    text = re.sub(r'[$€£¥₹\s]', '', text)

    # Remove percentage sign (preserve value)
    text = text.replace('%', '')

    # Remove commas
    text = text.replace(',', '')

    # Handle negative sign
    if text.startswith("-") or text.startswith("−"):
        is_negative = True
        text = text[1:]

    try:
        result = float(text)
        return -result if is_negative else result
    except (ValueError, TypeError):
        return None


def is_numeric_cell(value: str) -> bool:
    """Check if a cell value is numeric (after cleaning)."""
    return clean_numeric(value) is not None


def extract_tables_from_pdf(
    file_path: str,
    pages: str = "all",
) -> TableExtractionResult:
    """
    Extract all tables from a PDF document.

    Uses Camelot (lattice → stream) with Tabula as fallback.

    Args:
        file_path: Path to the PDF file.
        pages: Page specification (e.g., "all", "1,3,5", "1-5").

    Returns:
        TableExtractionResult with all extracted tables.
    """
    result = TableExtractionResult(file_path=file_path)

    if not os.path.exists(file_path):
        result.errors.append(f"File not found: {file_path}")
        return result

    tables = []

    # Strategy 1: Camelot lattice mode (bordered tables)
    try:
        tables = _extract_with_camelot(file_path, pages, flavor="lattice")
        logger.info("Camelot lattice extraction", tables_found=len(tables))
    except Exception as e:
        logger.warning("Camelot lattice failed", error=str(e))

    # Strategy 2: If no tables found, try Camelot stream mode (borderless)
    if not tables:
        try:
            tables = _extract_with_camelot(file_path, pages, flavor="stream")
            logger.info("Camelot stream extraction", tables_found=len(tables))
        except Exception as e:
            logger.warning("Camelot stream failed", error=str(e))

    # Strategy 3: Tabula fallback
    if not tables:
        try:
            tables = _extract_with_tabula(file_path, pages)
            logger.info("Tabula extraction", tables_found=len(tables))
        except Exception as e:
            logger.warning("Tabula failed", error=str(e))
            result.errors.append(f"All table extraction methods failed: {str(e)}")

    result.tables = tables
    result.total_tables = len(tables)

    # Process numeric values for each table
    for table in result.tables:
        table.numeric_rows = _parse_numeric_rows(table.rows)

    return result


def _extract_with_camelot(
    file_path: str,
    pages: str,
    flavor: str = "lattice",
) -> list[ExtractedTable]:
    """Extract tables using Camelot."""
    import camelot

    camelot_tables = camelot.read_pdf(
        file_path,
        pages=pages,
        flavor=flavor,
        suppress_stdout=True,
    )

    extracted = []
    for i, table in enumerate(camelot_tables):
        df = table.df

        # First row is usually headers
        headers = [str(h).strip() for h in df.iloc[0].values]
        rows = []
        for _, row in df.iloc[1:].iterrows():
            rows.append([str(v).strip() for v in row.values])

        extracted.append(ExtractedTable(
            table_id=i + 1,
            page_number=table.page,
            headers=headers,
            rows=rows,
            accuracy=table.accuracy,
            method=f"camelot_{flavor}",
        ))

    return extracted


def _extract_with_tabula(
    file_path: str,
    pages: str,
) -> list[ExtractedTable]:
    """Extract tables using Tabula (Java-based fallback)."""
    import tabula

    tabula_pages = pages if pages != "all" else "all"
    dfs = tabula.read_pdf(
        file_path,
        pages=tabula_pages,
        multiple_tables=True,
        pandas_options={"header": None},
    )

    extracted = []
    for i, df in enumerate(dfs):
        if df.empty:
            continue

        headers = [str(h).strip() for h in df.iloc[0].values]
        rows = []
        for _, row in df.iloc[1:].iterrows():
            rows.append([str(v).strip() if str(v) != "nan" else "" for v in row.values])

        extracted.append(ExtractedTable(
            table_id=i + 1,
            page_number=0,  # Tabula doesn't always report page numbers
            headers=headers,
            rows=rows,
            accuracy=0.0,
            method="tabula",
        ))

    return extracted


def _parse_numeric_rows(rows: list[list[str]]) -> list[list[float | None]]:
    """Parse all rows into numeric values where possible."""
    numeric_rows = []
    for row in rows:
        numeric_row = []
        for cell in row:
            numeric_row.append(clean_numeric(cell))
        numeric_rows.append(numeric_row)
    return numeric_rows


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python table_extractor.py <pdf_path>")
        sys.exit(1)

    result = extract_tables_from_pdf(sys.argv[1])
    print(f"\n{'='*60}")
    print(f"Extracted from: {result.file_path}")
    print(f"Total tables: {result.total_tables}")
    print(f"{'='*60}\n")

    for table in result.tables:
        print(f"--- Table {table.table_id} (Page {table.page_number}, {table.method}) ---")
        print(f"Headers: {table.headers}")
        print(f"Rows: {len(table.rows)}")
        print(f"Accuracy: {table.accuracy:.1f}%")
        for row in table.rows[:3]:
            print(f"  {row}")
        if len(table.rows) > 3:
            print(f"  ... ({len(table.rows) - 3} more rows)")
        print()
