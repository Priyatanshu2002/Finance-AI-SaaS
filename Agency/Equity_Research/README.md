# Module A: Equity Research Factory
> **Status:** Phase 2 (Active)
> **Output:** Initiation of Coverage Report + DCF Model

## Workflow
1.  **Ingestion:** Google Vertex AI (Gemini 1.5 Pro) reads 10-K/10-Q.
2.  **Spreading:** Google Document AI extracts financial tables to Excel.
3.  **Modeling:** Python Engine projects revenue/margins based on consensus.
4.  **Drafting:** Claude Opus 4.6 writes the Investment Thesis.

## File Structure
*   `/Input`: Drop 10-K PDFs here.
*   `/Output`: Final PDF Reports.
*   `runner.py`: Main execution script.
