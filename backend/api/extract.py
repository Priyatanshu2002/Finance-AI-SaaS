import os
import structlog
from fastapi import APIRouter, HTTPException, BackgroundTasks

from models.schemas import ExtractionResult, ProcessingStatus, FinancialStatement, LineItem, ValidationResults, AgentType
from services.pipeline_service import ExtractionPipelineService
from database.client import db

logger = structlog.get_logger()
router = APIRouter()

# In-memory store deprecated, now using Supabase via backend.database.client.db
# _extractions: dict[str, ExtractionResult] = {}

async def run_extraction_pipeline(document_id: str, file_path: str, agent_type: AgentType = AgentType.CLAUDE_SPECIALIST, extraction_db_id: str = None):
    """Background task to run the extraction pipeline."""
    try:
        service = ExtractionPipelineService(document_id, file_path, agent_type=agent_type, extraction_db_id=extraction_db_id)
        status = await service.run()
        
        if status.stage == "complete":
            # Map pipeline results back to the Pydantic model
            results = status.results
            statements_data = results.get("statements", {})
            
            # Helper to create FinancialStatement from standardized labels
            def build_statement(statement_type: str):
                line_items = []
                # Simple mapping for now
                for label, values in statements_data.items():
                    # This is naive; normally we'd check if the label belongs to the statement type
                    # But for now, we'll just put everything in if it has values
                    line_items.append(LineItem(
                        label=label.replace("_", " ").title(),
                        standardized_label=label,
                        values=values,
                        confidence=0.9
                    ))
                return FinancialStatement(periods=results.get("periods", []), line_items=line_items)

            # Update Supabase
            if extraction_db_id:
                final_result = ExtractionResult(
                    document_id=document_id,
                    status=ProcessingStatus.COMPLETED,
                    quality_score=results.get("quality_score", 0),
                    statements={
                        "income_statement": build_statement("income_statement"),
                        "balance_sheet": build_statement("balance_sheet"),
                        "cash_flow_statement": build_statement("cash_flow_statement"),
                    },
                    calculated_metrics=results.get("metrics", {}),
                    selected_agent=agent_type,
                    validation=ValidationResults(
                        quality_score=results.get("quality_score", 0),
                    )
                )
                await db.save_extraction({
                    "id": extraction_db_id,
                    "extraction_id": document_id, # Simplified for demo
                    "status": "completed",
                    "quality_score": results.get("quality_score", 0),
                    "structured_data": final_result.model_dump()
                })
            
            logger.info("Background extraction complete", document_id=document_id)
        else:
            if extraction_db_id:
                await db.save_extraction({"id": extraction_db_id, "status": "failed"})
            logger.error("Background extraction failed", document_id=document_id, errors=status.errors)
            
    except Exception as e:
        logger.error("Error in background pipeline", document_id=document_id, error=str(e))
        if extraction_db_id:
             await db.save_extraction({"id": extraction_db_id, "status": "failed"})

@router.post("/extract")
async def trigger_extraction(document_id: str, background_tasks: BackgroundTasks, agent_type: AgentType = AgentType.CLAUDE_SPECIALIST):
    """
    Trigger extraction pipeline on an uploaded document.
    """
    # Find the uploaded file in .tmp/uploads/
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", ".tmp", "uploads")
    file_path = None
    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            if f.startswith(document_id):
                file_path = os.path.join(upload_dir, f)
                break
    
    if not file_path:
        raise HTTPException(
            status_code=404,
            detail=f"Document file for {document_id} not found. Did you upload it?"
        )

    logger.info("Extraction triggered", document_id=document_id, file=file_path)

    # 1. Create Document record in Supabase (Mocked user_id/org_id for now)
    try:
        doc_uuid = await db.save_document({
            "uploaded_by": "00000000-0000-0000-0000-000000000000",
            "organization_id": "00000000-0000-0000-0000-000000000000",
            "filename": os.path.basename(file_path),
            "file_type": "pdf",
            "file_size_bytes": os.path.getsize(file_path),
            "storage_path": file_path
        })

        # 2. Create Extraction record
        extraction_db_id = await db.save_extraction({
            "document_id": doc_uuid,
            "extraction_id": document_id,
            "status": "processing",
            "selected_agent": agent_type,
            "structured_data": {"status": "starting"}
        })

        # 3. Start background task
        background_tasks.add_task(run_extraction_pipeline, document_id, file_path, agent_type=agent_type, extraction_db_id=extraction_db_id)

        return {
            "extraction_id": document_id,
            "document_id": doc_uuid,
            "status": "processing",
            "message": "Extraction pipeline started in background (Persisted to Supabase).",
        }
    except Exception as e:
        logger.error("Failed to initialize database records", error=str(e))
        raise HTTPException(status_code=500, detail="Database error during extraction initialization.")


@router.get("/extraction/{document_id}", response_model=ExtractionResult)
async def get_extraction_results(document_id: str):
    """
    Get extraction results from Supabase.
    """
    # Note: extraction_id in our URL maps to extraction_id column in DB
    try:
        res = db.client.table("extractions").select("*").eq("extraction_id", document_id).execute()
        if not res.data:
             raise HTTPException(status_code=404, detail=f"No extraction found for ID {document_id}")
        
        data = res.data[0]
        # Return the structured_data portion which is the ExtractionResult model
        return data.get("structured_data")
    except Exception as e:
        logger.error("Failed to query database", error=str(e))
        raise HTTPException(status_code=500, detail="Error retrieving result from database.")


@router.get("/agents")
async def list_agents():
    """
    List available specialized agents for financial analysis.
    """
    return [
        {
            "id": AgentType.CLAUDE_SPECIALIST,
            "name": "Claude Specialist",
            "description": "High-precision GAAP extraction and label mapping (Claude 3.5 Sonnet / Opus 4.6).",
            "capabilities": ["Precision Mapping", "Zero-Shot NER", "Semantic Alignment"],
            "cost_tier": "Premium"
        },
        {
            "id": AgentType.GEMINI_ARCHIVIST,
            "name": "Gemini Archivist",
            "description": "Best for multi-hundred page documents and rapid context retrieval (Gemini 1.5 Pro).",
            "capabilities": ["2M Token Window", "Fast Ingestion", "GCP Credits Safe"],
            "cost_tier": "Free (Credits)"
        },
        {
            "id": AgentType.DEEPSEEK_MATHEMATICIAN,
            "name": "DeepSeek Mathematician",
            "description": "Optimized for quantitative reasoning, formula validation, and stress-testing math.",
            "capabilities": ["Verifiable Math", "Chain-of-Thought Reasoning", "Quantitative Finance"],
            "cost_tier": "Economy"
        },
        {
            "id": AgentType.GPT_PROPHET,
            "name": "GPT Prophet",
            "description": "Strong generalist for predictive analysis, trend forecasting, and earnings narrative synthesis.",
            "capabilities": ["Trend Analysis", "Narrative Synthesis", "Market Baseline"],
            "cost_tier": "Standard"
        }
    ]
