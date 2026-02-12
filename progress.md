# Finance AI SaaS — Progress Log (`progress.md`)
> Activity log. What was done, errors encountered, test results. Updated after every meaningful task.

---

## 2026-02-12 — Session 1

### Protocol 0: Initialization

**00:02 IST** — Started B.L.A.S.T. Protocol 0
- Read `Planning/automated_workflows.json` (603 lines, 5 workflows)
- Read `Planning/finance_domain_problem_statements.json` (1,225 lines, 20 problem statements)

**00:05 IST** — Discovery Research
- Answered all 5 Discovery Questions through source analysis + web research
- Researched tech stacks, open-source tools, GitHub repos, debt sculpting methodologies
- Key tools identified: MinerU, PDF-Extract-Kit, Tabula, Camelot, FinGPT, OpenBB, QuantLib

**00:10 IST** — Blueprint Document Created
- Created `Planning/BLAST_Blueprint_Knowledge_Base.txt` (400+ lines, 10 sections)
- Covers: Discovery Answers, Data Schemas, Tech Stack, Architecture, Workflows, Competitive Landscape, Revenue Model, Timeline, Checklist, Shared Infrastructure

**00:12 IST** — NotebookLM Knowledge Base
- Created notebook: `Finance AI SaaS — B.L.A.S.T. Blueprint Knowledge Base`
- Notebook ID: `9278f9e8-be22-480b-a01d-8dc099654f74`
- Uploaded `BLAST_Blueprint_Knowledge_Base.txt` as source (processing complete)
- ⚠️ `.json` files not supported by NotebookLM — data already embedded in `.txt` source
- Initiated slide deck generation (detailed_deck format)

**00:20 IST** — Protocol 0 Memory Files
- User confirmed: Use **Claude Opus 4.6** instead of Gemini for LLM
- Created `gemini.md` — Project Constitution with schemas, rules, architecture
- Created `task_plan.md` — Detailed phase/goal/checklist tracker
- Created `findings.md` — Research discoveries and constraints
- Created `progress.md` — This activity log
- Updated blueprint to reflect Claude Opus 4.6

### Errors & Issues
| # | Issue | Status | Resolution |
|---|-------|--------|------------|
| 1 | NotebookLM rejects `.json` uploads | Resolved | Data embedded in `.txt` blueprint instead |
| 2 | Slide deck generation taking >10 min | Resolved | Available at notebook URL when ready |

### Tests Run
- None yet (Protocol 0 is initialization only — no code to test)

---

**00:25 IST** — User Decisions
- User confirmed: **No OpenAI at all** — Claude Opus 4.6 is sole LLM provider
- Removed all OpenAI references from `gemini.md`, `findings.md`, `BLAST_Blueprint_Knowledge_Base.txt`

**00:32 IST** — Google Stitch + Timeline Compression
- User asked about frontend automation via **Google Stitch**
- Researched: Stitch is AI-powered UI tool (Google Labs, I/O 2025), exports React/HTML + Tailwind CSS
- User approved: Incorporate Stitch, compress timeline to **6 months for Products 1–3**
- Updated all files: `gemini.md`, `task_plan.md`, `findings.md`, `progress.md`, `BLAST_Blueprint_Knowledge_Base.txt`
- Key changes: Vanilla CSS → Tailwind CSS (Stitch default), added Stitch to tech stack, month-by-month plan with parallel frontend/backend tracks
- GCP trial credit (₹26K) noted for infrastructure

---

## 2026-02-12 — Session 2

### Phase 1: Pipeline Integration

**01:45 IST** — Project Status Review
- Verified 5 core extraction tools in `tools/`
- Verified FastAPI backend scaffolding in `backend/`
- Identified missing unified service orchestrator

**01:50 IST** — Implementation Plan Approved
- User approved plan for `ExtractionPipelineService` integration

**02:00 IST** — Extraction Pipeline Service Created
- Created `backend/services/pipeline_service.py`
- Implemented 7-stage orchestration (OCR → Tables → NER → Norm → Valid → Metrics)
- Added numeric cell cleaning and period alignment logic
- Added placeholder for Claude Opus 4.6 (Stage 4 NER)

**02:10 IST** — API Integration & Async Tasks
- Updated `backend/api/extract.py`
- Triggering pipeline via `BackgroundTasks` in FastAPI
- Implemented polling mechanism at `GET /api/extraction/{document_id}`
- Mapped pipeline output to Pydantic `ExtractionResult` models

### Errors & Issues (Updated)
| # | Issue | Status | Resolution |
|---|-------|--------|------------|
| 3 | In-memory store used for /api/extract | In Progress | Transition to Supabase/PostgreSQL planned |
| 4 | Tesseract/Poppler Docker verification | In Progress | Need sample PDF to test end-to-end |

### Tests Run
- Verified `pipeline_service.py` logic via CLI simulation
- Verified FastAPI endpoint routing and background task initialization
