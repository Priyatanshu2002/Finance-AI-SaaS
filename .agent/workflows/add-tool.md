---
description: Add a new extraction/analysis tool to the pipeline
---

# Add a New Tool

Checklist for creating a new tool in `tools/`, integrating it into the pipeline, and exposing it via the API.

## Steps

1. **Create the tool file** at `tools/<tool_name>.py`. Follow this structure:
   ```python
   """
   Finance AI SaaS — <Tool Name>
   <Brief description of what this tool does.>
   """

   import structlog

   logger = structlog.get_logger()


   class <ToolName>:
       """<Description>"""

       def __init__(self, config: dict | None = None):
           self.config = config or {}

       async def process(self, input_data: dict) -> dict:
           """
           Main processing method.

           Args:
               input_data: Dictionary containing the data to process.

           Returns:
               Dictionary with processed results.
           """
           logger.info("<tool_name>.process.start", doc_id=input_data.get("document_id"))
           try:
               # Implementation here
               result = {}
               logger.info("<tool_name>.process.complete")
               return {"status": "success", "data": result}
           except Exception as e:
               logger.error("<tool_name>.process.failed", error=str(e))
               return {"status": "error", "error": str(e)}
   ```

2. **Register in the pipeline service** (`backend/services/pipeline_service.py`):
   - Import the new tool class
   - Add it to the pipeline stages list
   - Define where it runs in the pipeline order

3. **Add any new dependencies** to `backend/requirements.txt`.

4. **Create or update Pydantic models** in `backend/models/` if the tool has new input/output schemas.

5. **Add API endpoint** (if the tool needs direct access):
   - Create `backend/api/<tool_name>.py` with a FastAPI router
   - Register the router in `backend/main.py`

6. **Test the tool**:
   - Write unit tests in `backend/tests/test_<tool_name>.py`
   - Run: `pytest backend/tests/test_<tool_name>.py -v`
   - Run the full extraction pipeline smoke test (see `/test-extraction` workflow)

## Existing Tools for Reference

| Tool                      | File                        | Purpose                          |
|---------------------------|-----------------------------|----------------------------------|
| OCR Extractor             | `tools/ocr_extractor.py`    | Text extraction from scanned PDFs|
| Table Extractor           | `tools/table_extractor.py`  | Tabular data detection           |
| Financial Spreader        | `tools/financial_spreader.py`| Statement normalization          |
| Validation Engine         | `tools/validation_engine.py`| Cross-statement validation       |
| Metric Calculator         | `tools/metric_calculator.py`| Financial ratio calculations     |
