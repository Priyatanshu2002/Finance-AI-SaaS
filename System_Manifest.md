# System Manifest: Universal Financial Analysis System
> **Version:** 1.0.0 (2026-02-15)
> **Architecture:** Event-Driven Microservices (Python/Next.js)
> **AI Stack:** Hybrid (Gemini 1.5 Pro + Claude Opus 4.6)

---

## 1. System Overview
This is an automated investment banking platform designed to produce institutional-grade financial analysis at scale. It replaces the "SaaS-only" vision with a **Service-First Architecture** that powers both internal agency operations and external API consumption.

### Core Philosophy
*   **Data First:** If we can't ingest it (PDF/Excel) perfectly, we can't analyze it.
*   **Human-in-the-Loop:** AI drafts, Humans verify. No "black box" numbers.
*   **Module Independence:** Equity Research can run without LBO. CIM can run without Scouting.

---

## 2. Module Definition

### 🟢 Module A: Equity Research (`/Agency/Equity_Research`)
*   **Goal:** "Initiation of Coverage" Reports (Public Markets).
*   **Input:** 10-K, 10-Q, Transcripts (EDGAR/SeekingAlpha).
*   **Process:** Gemini Ingest -> Ratio Analysis (Excel) -> Opus Thesis -> Report.
*   **Output:** PDF Report + DCF Model.

### 🔵 Module B: LBO & Valuation (`/Agency/LBO_Valuation`)
*   **Goal:** Private Equity Deal Modeling.
*   **Input:** Private P&L, Cap Table, Debt Terms.
*   **Process:** Spreading -> LBO Engine (Python) -> Sensitivity Tables -> Inv. Memo.
*   **Output:** LBO Model (Excel) + Memo (Word).

### 🟠 Module C: The CIM Factory (`/Agency/CIM_Factory`)
*   **Goal:** Sell-Side M&A Marketing Materials.
*   **Input:** Data Room (Tax Returns, Ops Manual).
*   **Process:** Ingest -> Teaser -> Adjusted EBITDA -> CIM Draft -> Polish.
*   **Output:** Confidential Information Memorandum (40-60 pages).

### 🟣 Module D: Deal Scouting (`/Agency/Deal_Scouting`)
*   **Goal:** Origination & Lead Gen.
*   **Input:** Firecrawl Scraper parameters.
*   **Process:** Scrape -> Enrich (Opus) -> Score -> CRM Load.
*   **Output:** Qualified Deal Flow List.

---

## 3. Directory Structure (The "Map")

```
/Finance AI SaaS
├── _Archive/                 # Legacy SaaS Plans (Pre-Feb 2026)
├── Agency/                   # The "Universal Factory"
│   ├── CIM_Factory/          # Module C (Sell-Side)
│   ├── Deal_Scouting/        # Module D (Origination)
│   ├── Equity_Research/      # Module A (Public Markets)
│   ├── LBO_Valuation/        # Module B (Private Equity)
│   ├── Shared_Lib/           # Common Python Scripts (Spreader, PDF Parser)
│   └── deal_log.json         # Master Tracker
├── backend/                  # FastAPI / Python Services
├── frontend/                 # Next.js / Stitch UI
├── tools/                    # Core Utilities (Supabase, Scraping)
└── System_Manifest.md        # THIS FILE
```

---

## 4. The 2026 Tech Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Ingestion (Reasoning)** | **Google Vertex AI (Gemini 1.5 Pro)** | **2M Token Multimodal Context.** "Sees" the whole document for context and cross-referencing. |
| **Ingestion (Precision)** | **Google Document AI (Vision)** | **Specialized Table Parser.** Native Google Cloud Vision tech to extract pixel-perfect financial tables from messy PDFs. |
| **Reasoning** | **Claude Opus 4.6** | Use for "Banker Prose" and nuanced qualitative analysis. |
| **Modeling** | **Claude Excel Plugin** | Generating and formatting complex Excel models. |
| **Database** | **Supabase (PostgreSQL)** | Storing "Spread" financials and deal metadata. |
| **Frontend** | **Google Stitch (React)** | Internal Dashboards for Analysts to review/approve. |

---

## 5. Automation Protocols
1.  **The "Freeze" Rule:** Financials must be chemically frozen (approved by human) before Narrative generation begins.
2.  **No Math LLMs:** All calculations (CAGR, Margins, IRR) must be done in Python or Excel formulas, never by LLM tokens.
3.  **Source Traceability:** Every number in a report must cite its source file (e.g., "Source: 2024 Tax Return, Pg 4").
