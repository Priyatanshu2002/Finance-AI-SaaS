
import sys
import os
from unittest.mock import MagicMock

# Add parent dir to path
sys.path.append(os.getcwd())

# Mock heavy dependencies to test logic without environment issues
sys.modules["fitz"] = MagicMock()
sys.modules["camelot"] = MagicMock()
sys.modules["tabula"] = MagicMock()
sys.modules["cv2"] = MagicMock()
sys.modules["supabase"] = MagicMock()
sys.modules["asyncpg"] = MagicMock()
sys.modules["sqlalchemy"] = MagicMock()
sys.modules["redis"] = MagicMock()
sys.modules["google.cloud"] = MagicMock() # Mock GCP

try:
    # Need to mock backend.database.client before importing pipeline_service
    # creating a dummy module for backend.database.client
    # db object needs client attibute
    db_mock = MagicMock()
    db_mock.client = MagicMock() # supabase client mock
    
    # We can inject this into sys.modules if needed, but since we are running check
    # let's try importing. pipeline_service imports: "from backend.database.client import db"
    
    # We might need to mock backend.database first if it doesn't exist or has issues
    # Let's see if we can just rely on sys.modules mocking for external libs
    
    from backend.services.pipeline_service import ExtractionPipelineService
    print("Successfully imported ExtractionPipelineService")
    
    from backend.models.schemas import AgentType
    
    service = ExtractionPipelineService("test_id", "dummy.pdf", agent_type=AgentType.CLAUDE_SPECIALIST)
    print("Successfully initialized service with CLAUDE_SPECIALIST")
    
    import inspect
    if inspect.iscoroutinefunction(service._run_claude_logic):
         print("Verified _run_claude_logic is async")

except Exception as e:
    # Print full traceback for debugging
    import traceback
    traceback.print_exc()
    print(f"Failed: {e}")
    sys.exit(1)
