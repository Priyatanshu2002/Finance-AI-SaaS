# Finance AI SaaS — Task Plan (`task_plan.md`)
> Phases, goals, and checklists. Updated as work progresses.
> **Timeline: 6 months → Products 1–3 | Frontend via Google Stitch**

---

## Current Focus: Month 1 — Product 1 (Financial Data Extraction Engine)

---

## Protocol 0: Initialization ✅
- [x] Discovery Questions answered
- [x] Blueprint knowledge base created
- [x] NotebookLM notebook set up
- [x] `gemini.md` — Project Constitution created
- [x] `task_plan.md` — This file created
- [x] `findings.md` — Research log created
- [x] `progress.md` — Activity log created
- [x] LLM set to Claude Opus 4.6 (sole provider, no OpenAI)
- [x] Google Stitch added for frontend automation
- [x] Timeline compressed to 6 months (Products 1–3)

---

## Month 1–2: Product 1 — Financial Data Extraction Engine

### 1.1 Architecture Setup ✅
- [x] Write `architecture/extraction_pipeline.md` SOP
- [x] Define extraction stages (Ingestion → OCR → Table → NER → Normalize → Validate → Output)
- [x] Map edge cases (scanned PDFs, multi-language, multi-period statements)

### 1.2 Project Scaffolding ✅
- [x] Initialize Next.js 15 frontend (`frontend/`)
- [x] Initialize Python FastAPI backend (`backend/`)
- [x] Create `docker-compose.yml` for local development
- [x] Configure `.env` with API keys (Anthropic, Supabase, GCP)
- [ ] Set up Supabase project (PostgreSQL + Auth + pgvector)

### 1.3 Core Tools (Layer 3 — Python) ✅
- [x] `tools/ocr_extractor.py` — OCR and text extraction
- [x] `tools/table_extractor.py` — Table detection and data extraction
- [ ] `tools/financial_ner.py` — Financial named entity recognition (Claude Opus 4.6 Placeholder)
- [x] `tools/financial_spreader.py` — Statement normalization
- [x] `tools/validation_engine.py` — Cross-statement validation
- [x] `tools/metric_calculator.py` — Financial ratio calculations

### 1.4 API Layer
- [x] `POST /api/upload` — Document upload endpoint
- [x] `GET /api/extraction/{id}` — Get extraction results
- [ ] `GET /api/documents` — List user documents
- [x] `POST /api/extract` — Trigger extraction (Background Task Integrated)
- [ ] WebSocket for real-time progress updates

### 1.5 Frontend — via Google Stitch
- [ ] Define screen descriptions for Stitch
- [ ] Generate in Stitch: Auth flow (login, signup, org management)
- [ ] Generate in Stitch: Upload page with drag-and-drop
- [ ] Generate in Stitch: Processing status with progress bar
- [ ] Generate in Stitch: Extraction results viewer
- [ ] Export React/HTML → integrate into Next.js
- [ ] Wire UI components to API endpoints

---

## Month 2–4: Product 2 — CRE Underwriting Accelerator

### 2.1 Core Tools
- [ ] `tools/rent_roll_parser.py` — CRE rent roll extraction
- [ ] `tools/pro_forma_builder.py` — Pro forma model construction
- [ ] `tools/market_comp_analyzer.py` — Market comparable analysis
- [ ] `tools/report_generator.py` — Investment memo / PDF report generation

### 2.2 API Layer
- [ ] `POST /api/cre/upload` — Rent roll / OM upload
- [ ] `GET /api/cre/proforma/{id}` — Get pro forma results
- [ ] `POST /api/cre/scenarios` — Run scenario analysis
- [ ] `GET /api/cre/memo/{id}` — Get investment memo

### 2.3 Frontend — via Google Stitch
- [ ] Generate in Stitch: CRE underwriting dashboard
- [ ] Generate in Stitch: Pro forma viewer with scenario toggle
- [ ] Generate in Stitch: Investment memo preview
- [ ] Generate in Stitch: Export flow (PDF, Excel)
- [ ] Integrate + wire to CRE API endpoints

---

## Month 4–6: Product 3 — Project Finance Modeling Platform

### 3.1 Core Tools
- [ ] `tools/debt_sculpting.py` — Debt sculpting engine (DSCR/LLCR)
- [ ] `tools/construction_drawdown.py` — Construction phase drawdown
- [ ] `tools/multi_currency.py` — Multi-currency normalization
- [ ] `tools/scenario_engine.py` — Monte Carlo / sensitivity analysis
- [ ] `tools/lender_report.py` — Lender pack generation

### 3.2 API Layer
- [ ] `POST /api/pf/upload` — Term sheet / IM upload
- [ ] `GET /api/pf/model/{id}` — Get financial model
- [ ] `POST /api/pf/scenarios` — Run scenarios
- [ ] `GET /api/pf/lender-pack/{id}` — Generate lender report

### 3.3 Frontend — via Google Stitch
- [ ] Generate in Stitch: PF model builder dashboard
- [ ] Generate in Stitch: Debt sculpting visualization
- [ ] Generate in Stitch: Scenario comparison view
- [ ] Generate in Stitch: Lender report viewer
- [ ] Integrate + wire to PF API endpoints

---

## Month 6: Polish + Deployment

### Hardening
- [ ] End-to-end testing all 3 products
- [ ] Performance optimization
- [ ] Security audit (encryption, RBAC, audit trails)
- [ ] Error handling + self-annealing protocol verification

### Deployment
- [ ] Deploy to Google Cloud Run (GCP trial credit)
- [ ] Set up CI/CD (GitHub Actions)
- [ ] Configure custom domain
- [ ] Set up monitoring (Sentry + Cloud Monitoring)

---

## Post-Launch (Month 7+)
- [ ] Product 4: CIM Generation Engine
- [ ] Product 5: M&A Due Diligence Pipeline
- [ ] Stripe billing integration
- [ ] Design partner onboarding
