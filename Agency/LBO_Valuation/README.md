# Module B: LBO & Valuation Engine
> **Status:** Phase 4 (Planned)
> **Output:** LBO Model (Excel) + Investment Committee Memo

## Workflow
1.  **Spreading:** Ingest Private P&L (Excel/PDF) -> Adjusted EBITDA.
2.  **Modeling:** LBO Engine calculates IRR, MOIC at defined entry/exit multiples.
3.  **Sensitivity:** Generates "Football Field" valuation charts.
4.  **Drafting:** Opus writes the "Risks & Mitigants" section.

## File Structure
*   `lbo_engine.py`: Core calculation logic.
*   `/Deals`: Deal-specific folders.
