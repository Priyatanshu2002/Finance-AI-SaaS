---
description: Smoke test the document extraction pipeline end-to-end
---

# Test Extraction Pipeline

End-to-end smoke test: upload a PDF → trigger extraction → check results.

## Prerequisites

- Backend running on `http://localhost:8000` (via Docker or standalone)
- A test PDF file available (financial statement, bank statement, etc.)

## Steps

1. Upload a test document:
```
curl -X POST http://localhost:8000/api/upload -F "file=@<path_to_test_pdf>"
```
Replace `<path_to_test_pdf>` with the actual file path.
Save the returned `document_id` from the response.

2. Trigger extraction on the uploaded document:
```
curl -X POST http://localhost:8000/api/extract -H "Content-Type: application/json" -d "{\"document_id\": \"<document_id>\"}"
```
Replace `<document_id>` with the ID from step 1.
This returns a `task_id` and starts background processing.

3. Check extraction results:
```
curl http://localhost:8000/api/extraction/<document_id>
```
The response includes status (`pending`, `processing`, `completed`, `failed`) and extracted data.

4. List all documents to verify the upload appears:
```
curl http://localhost:8000/api/documents
```

## Expected Pipeline Stages

The extraction pipeline runs these stages in order:

1. **Ingestion** — Read and parse the PDF
2. **OCR** — Extract text from scanned/image-based pages
3. **Table Extraction** — Detect and extract tabular data
4. **Financial Spreading** — Normalize to standard statement format
5. **Validation** — Cross-validate extracted figures
6. **Metrics** — Calculate financial ratios

## Troubleshooting

- **Upload fails**: Check that `python-multipart` is installed and the `.tmp` directory exists.
- **Extraction hangs**: Check backend logs with `docker-compose logs -f backend`.
- **OCR returns empty**: Verify Tesseract is installed (`tesseract --version`).
