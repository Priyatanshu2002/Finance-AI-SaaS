# Extraction Pipeline — Architecture SOP

> **Layer 1 SOP** — Defines HOW the financial data extraction workflow operates.
> Update this file BEFORE changing any tools in `tools/`.

---

## Goal
Extract structured financial data from any uploaded document (PDF, DOCX, XLSX, scanned image) and output a validated, normalized JSON payload conforming to the `gemini.md` output schema.

---

## Pipeline Stages

```
Document Upload
     │
     ▼
┌─────────────┐
│ 1. INGESTION │  Accept file, validate format, store original
└──────┬──────┘
       ▼
┌─────────────┐
│ 2. OCR       │  Extract raw text + coordinates from every page
└──────┬──────┘
       ▼
┌──────────────────┐
│ 3. TABLE EXTRACT │  Detect and extract all tables as structured arrays
└──────┬───────────┘
       ▼
┌──────────────────┐
│ 4. FINANCIAL NER │  Identify financial line items, periods, currencies
└──────┬───────────┘
       ▼
┌──────────────────┐
│ 5. NORMALIZATION │  Map to standardized labels, align periods, normalize currency
└──────┬───────────┘
       ▼
┌──────────────────┐
│ 6. VALIDATION    │  Cross-check statements, flag anomalies, score confidence
└──────┬───────────┘
       ▼
┌──────────────────┐
│ 7. OUTPUT        │  Return structured JSON + calculated metrics
└──────────────────┘
```

---

## Stage Details

### Stage 1: Ingestion
- **Tool**: FastAPI upload endpoint
- **Input**: File (PDF, DOCX, XLSX, CSV, PNG/JPG)
- **Logic**:
  1. Validate file type and size (max 50MB)
  2. Generate `document_id` (UUID)
  3. Store original file in Cloud Storage (immutable)
  4. Create DB record with metadata
  5. Queue for processing
- **Output**: `document_id`, processing status
- **Edge cases**:
  - Password-protected files → reject with error message
  - Corrupt files → reject with error message
  - Duplicate uploads → detect via file hash, warn user

### Stage 2: OCR / Text Extraction
- **Tool**: `tools/ocr_extractor.py`
- **Input**: Document file path
- **Logic**:
  1. Check if PDF has selectable text (native PDF)
  2. If native → extract text with PyMuPDF (fast, preserves layout)
  3. If scanned → run Tesseract OCR (or Cloud Vision API for high accuracy)
  4. For each page, output text blocks with bounding box coordinates
- **Output**: List of `{page, text, coordinates}` objects
- **Edge cases**:
  - Mixed native + scanned pages → handle per-page
  - Multi-column layouts → detect and split columns
  - Rotated pages → detect orientation and correct
  - Low-quality scans → flag low confidence, suggest re-upload

### Stage 3: Table Extraction
- **Tool**: `tools/table_extractor.py`
- **Input**: Document file path + OCR text output
- **Logic**:
  1. Detect table regions using Camelot's lattice mode (for bordered tables)
  2. Fall back to Camelot stream mode (for borderless tables)
  3. Fall back to Tabula if Camelot fails
  4. For each table: extract headers, data rows, merge multi-row headers
  5. Clean numeric values (remove $, commas, handle parentheses as negative)
- **Output**: List of tables as `{headers, rows, page, coordinates}` objects
- **Edge cases**:
  - Tables spanning multiple pages → detect and merge
  - Nested tables → flatten to single level
  - Tables with merged cells → expand merged cells
  - No tables found → skip to NER on raw text

### Stage 4: Financial NER (Named Entity Recognition)
- **Tool**: `tools/financial_ner.py` (uses Claude Opus 4.6 for NLP)
- **Input**: Extracted tables + text
- **Logic**:
  1. Send structured table data to Claude with financial NER prompt
  2. Claude identifies: line item labels, period headers, currency, units
  3. Claude classifies document type (income statement, balance sheet, CF, mixed)
  4. Map each extracted value to: `{label, value, period, currency, confidence}`
- **Output**: Classified and labeled financial data
- **LLM rules**:
  - Claude does CLASSIFICATION and LABELING only
  - Claude does NOT compute or transform numbers
  - All numeric values are passed through as-is from extraction
  - Confidence score assigned per field

### Stage 5: Normalization
- **Tool**: `tools/financial_spreader.py`
- **Input**: NER-labeled financial data
- **Logic**:
  1. Map extracted labels → standardized taxonomy:
     - "Net Sales", "Total Revenue", "Revenue" → `total_revenue`
     - "Cost of Goods Sold", "COGS", "Cost of Revenue" → `cost_of_revenue`
     - etc. (100+ mapping rules)
  2. Align fiscal periods (handle FY vs calendar year, quarterly data)
  3. Normalize to specified currency (if multi-currency)
  4. Separate into statement types: income_statement, balance_sheet, cash_flow
- **Output**: Normalized financial statements matching `gemini.md` schema
- **Edge cases**:
  - Ambiguous labels → flag for human review with top-3 suggestions
  - Missing line items → mark as null, don't impute
  - Different accounting standards (GAAP vs IFRS) → detect and note

### Stage 6: Validation
- **Tool**: `tools/validation_engine.py`
- **Input**: Normalized financial statements
- **Logic**:
  1. Balance sheet check: Total Assets = Total Liabilities + Total Equity (±1% tolerance)
  2. Income statement check: Revenue - Expenses = Net Income (verify arithmetic)
  3. Cash flow reconciliation: Beginning Cash + Net Cash = Ending Cash
  4. Cross-statement: Net Income flows correctly to CF and BS
  5. Assign overall quality_score (0-100)
  6. Flag items below 95% confidence for human review
- **Output**: Validation results + quality score + flagged items
- **Thresholds**:
  - quality_score ≥ 90 → auto-approve
  - quality_score 70-89 → flag for review, show to user
  - quality_score < 70 → reject, suggest re-upload or manual entry

### Stage 7: Output
- **Input**: Validated, normalized data
- **Logic**:
  1. Calculate financial metrics (via `tools/metric_calculator.py`)
  2. Assemble final JSON payload per `gemini.md` output schema
  3. Store in PostgreSQL
  4. Return to API caller / update dashboard
- **Output**: Complete extraction result with metrics

---

## Confidence Scoring

| Confidence Level | Range | Action |
|-----------------|-------|--------|
| High | 95-100% | Auto-approve, no review needed |
| Medium | 80-94% | Show to user with highlight, allow correction |
| Low | 50-79% | Flag for mandatory human review |
| Failed | <50% | Reject field, request manual entry |

---

## Error Handling (Self-Annealing)

When any stage fails:
1. Log the error with full context (stage, input, stack trace)
2. Attempt retry with alternative method:
   - OCR fail → switch from Tesseract to Cloud Vision
   - Table extraction fail → switch from Camelot to Tabula
   - NER fail → retry with different Claude prompt
3. If retry fails → mark document as `needs_manual_review`
4. Update this SOP with the learning

---

## Human Review Checkpoints

| Checkpoint | Trigger | What User Sees |
|-----------|---------|---------------|
| Document type | Low confidence classification | "Is this an income statement or balance sheet?" |
| Line item mapping | Ambiguous label | "We mapped 'Net Sales' to 'Revenue'. Correct?" |
| Numeric extraction | Low confidence on a number | "We extracted $1,234,567. Verify against source." |
| Validation failure | Balance sheet doesn't balance | "Assets ≠ Liabilities + Equity. Please review." |
