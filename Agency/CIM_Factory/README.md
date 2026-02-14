# Module C: The CIM Factory
> **Status:** Phase 1 (Live)
> **Output:** Confidential Information Memorandum (CIM)

## Workflow
1.  **Ingestion:** Google Drive API triggers ingestion of Client Data Room.
2.  **Analysis:** Gemini 1.5 Pro extracts "Investment Highlights".
3.  **Spreading:** Google Sheets API normalizes P&L.
4.  **Drafting:** Claude Opus 4.6 writes narrative sections.
5.  **Assembly:** Word Template (Banker Style).

## File Structure
*   `/Deals`: One folder per client deal (e.g., `DL-001`).
*   `/Templates`: Master Word/Excel templates.
