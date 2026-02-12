"""
OCR Extractor — Stage 2 of Extraction Pipeline
Extracts text and coordinates from PDF documents.

Strategy:
1. Try native text extraction (PyMuPDF) — fast, high fidelity
2. Fall back to OCR (Tesseract) for scanned pages
3. Return page-level text blocks with bounding boxes
"""

import io
import os
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
import structlog

logger = structlog.get_logger()


@dataclass
class TextBlock:
    """A block of text extracted from a page."""
    text: str
    page_number: int
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    confidence: float = 1.0
    method: str = "native"  # "native" or "ocr"


@dataclass
class PageExtraction:
    """Extraction results for a single page."""
    page_number: int
    full_text: str = ""
    blocks: list[TextBlock] = field(default_factory=list)
    is_scanned: bool = False
    method: str = "native"


@dataclass
class DocumentExtraction:
    """Complete extraction results for a document."""
    file_path: str
    total_pages: int = 0
    pages: list[PageExtraction] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Concatenate all page text."""
        return "\n\n".join(p.full_text for p in self.pages if p.full_text)


def extract_text_from_pdf(file_path: str) -> DocumentExtraction:
    """
    Extract text from a PDF file.

    Uses PyMuPDF for native PDFs (text-selectable).
    Falls back to Tesseract OCR for scanned pages.

    Args:
        file_path: Path to the PDF file.

    Returns:
        DocumentExtraction with page-level text and coordinates.
    """
    result = DocumentExtraction(file_path=file_path)

    if not os.path.exists(file_path):
        result.errors.append(f"File not found: {file_path}")
        return result

    try:
        doc = fitz.open(file_path)
        result.total_pages = len(doc)

        logger.info("Starting PDF extraction", file=file_path, pages=len(doc))

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_extraction = _extract_page(page, page_num + 1)
            result.pages.append(page_extraction)

        doc.close()

        logger.info(
            "PDF extraction complete",
            file=file_path,
            pages=result.total_pages,
            scanned_pages=sum(1 for p in result.pages if p.is_scanned),
        )

    except Exception as e:
        error_msg = f"Failed to extract text from PDF: {str(e)}"
        logger.error(error_msg, file=file_path)
        result.errors.append(error_msg)

    return result


def _extract_page(page: fitz.Page, page_number: int) -> PageExtraction:
    """Extract text from a single page."""
    extraction = PageExtraction(page_number=page_number)

    # Try native text extraction first
    text_dict = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)
    blocks = text_dict.get("blocks", [])

    native_text_blocks = []
    for block in blocks:
        if block.get("type") == 0:  # Text block
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span.get("text", "")
                block_text += "\n"

            block_text = block_text.strip()
            if block_text:
                bbox = block.get("bbox", (0, 0, 0, 0))
                native_text_blocks.append(TextBlock(
                    text=block_text,
                    page_number=page_number,
                    x=bbox[0],
                    y=bbox[1],
                    width=bbox[2] - bbox[0],
                    height=bbox[3] - bbox[1],
                    confidence=1.0,
                    method="native",
                ))

    # Check if page has meaningful text
    full_text = "\n".join(b.text for b in native_text_blocks)
    if len(full_text.strip()) > 50:
        # Native extraction succeeded
        extraction.full_text = full_text
        extraction.blocks = native_text_blocks
        extraction.is_scanned = False
        extraction.method = "native"
    else:
        # Page is likely scanned — use OCR
        extraction = _ocr_page(page, page_number)

    return extraction


def _ocr_page(page: fitz.Page, page_number: int) -> PageExtraction:
    """
    OCR a scanned page using Tesseract.

    Falls back gracefully if Tesseract is not installed.
    """
    extraction = PageExtraction(
        page_number=page_number,
        is_scanned=True,
        method="ocr",
    )

    try:
        import pytesseract
        from PIL import Image

        # Render page to image at 300 DPI for good OCR quality
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))

        # Run Tesseract OCR with detailed output
        ocr_data = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DICT
        )

        blocks = []
        current_block = ""
        current_block_num = -1
        block_coords = {"x": 0, "y": 0, "w": 0, "h": 0}

        for i in range(len(ocr_data["text"])):
            text = ocr_data["text"][i].strip()
            block_num = ocr_data["block_num"][i]
            conf = int(ocr_data["conf"][i])

            if block_num != current_block_num and current_block:
                # Save previous block
                blocks.append(TextBlock(
                    text=current_block.strip(),
                    page_number=page_number,
                    x=block_coords["x"],
                    y=block_coords["y"],
                    width=block_coords["w"],
                    height=block_coords["h"],
                    confidence=conf / 100.0,
                    method="ocr",
                ))
                current_block = ""

            current_block_num = block_num
            if text and conf > 30:
                current_block += text + " "
                block_coords = {
                    "x": ocr_data["left"][i],
                    "y": ocr_data["top"][i],
                    "w": ocr_data["width"][i],
                    "h": ocr_data["height"][i],
                }

        # Don't forget the last block
        if current_block.strip():
            blocks.append(TextBlock(
                text=current_block.strip(),
                page_number=page_number,
                x=block_coords["x"],
                y=block_coords["y"],
                width=block_coords["w"],
                height=block_coords["h"],
                confidence=0.8,
                method="ocr",
            ))

        extraction.blocks = blocks
        extraction.full_text = "\n".join(b.text for b in blocks)

        logger.info(
            "OCR extraction complete",
            page=page_number,
            blocks=len(blocks),
        )

    except ImportError:
        logger.warning("Tesseract not available — skipping OCR", page=page_number)
        extraction.full_text = ""
        extraction.blocks = []

    except Exception as e:
        logger.error("OCR failed", page=page_number, error=str(e))
        extraction.full_text = ""

    return extraction


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python ocr_extractor.py <pdf_path>")
        sys.exit(1)

    result = extract_text_from_pdf(sys.argv[1])
    print(f"\n{'='*60}")
    print(f"Extracted from: {result.file_path}")
    print(f"Total pages: {result.total_pages}")
    print(f"Scanned pages: {sum(1 for p in result.pages if p.is_scanned)}")
    print(f"{'='*60}\n")

    for page in result.pages:
        print(f"--- Page {page.page_number} ({page.method}) ---")
        print(page.full_text[:500])
        print()
