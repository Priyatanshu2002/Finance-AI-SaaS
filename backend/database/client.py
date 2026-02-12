import os
from supabase import create_client, Client
import structlog

logger = structlog.get_logger()

class DatabaseClient:
    """
    Supabase wrapper for Finance AI SaaS persistence.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseClient, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            logger.error("Database initialization failed: Missing Supabase credentials")
            self.client = None
        else:
            self.client = create_client(url, key)
            logger.info("Supabase client initialized")

    async def save_document(self, doc_data: dict) -> str:
        """Insert a document record and return its UUID."""
        try:
            res = self.client.table("documents").insert(doc_data).execute()
            return res.data[0]["id"]
        except Exception as e:
            logger.error("Failed to save document", error=str(e))
            raise

    async def save_extraction(self, extraction_data: dict) -> str:
        """Insert or update an extraction result."""
        try:
            # Upsert using extraction_id as unique constraint (requires DB configuration)
            res = self.client.table("extractions").upsert(
                extraction_data, on_conflict="extraction_id"
            ).execute()
            return res.data[0]["id"]
        except Exception as e:
            logger.error("Failed to save extraction", error=str(e))
            raise

    async def get_extraction_by_document(self, document_id: str):
        """Fetch the latest extraction for a document."""
        try:
            res = self.client.table("extractions")\
                .select("*")\
                .eq("document_id", document_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error("Failed to fetch extraction", error=str(e))
            return None

    def log_audit(self, user_id: str, action: str, resource_type: str, resource_id: str, context: dict = None):
        """Log an audit entry."""
        try:
            audit_data = {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "context": context or {}
            }
            self.client.table("audit_logs").insert(audit_data).execute()
        except Exception as e:
            logger.warning("Audit logging failed", error=str(e))

# Global instance
db = DatabaseClient()
