# Finance AI SaaS — Project Constitution (`gemini.md`)
> **This file is LAW.** Only update when a schema changes, a rule is added, or architecture is modified.

---

## 🏛️ Project Identity

| Field | Value |
|-------|-------|
| **Project Name** | Finance AI SaaS Platform |
| **Protocol** | B.L.A.S.T. (Blueprint, Link, Architect, Stylize, Trigger) |
| **Architecture** | A.N.T. 3-Layer (Architecture → Navigation → Tools) |
| **LLM** | Anthropic Claude Opus 4.6 (sole provider — no OpenAI) |
| **UI Design** | Google Stitch (AI-powered UI generation) |
| **Created** | 2026-02-12 |
| **Status** | Protocol 0 — Initialization |

---

## 📦 Product Suite

| # | Product | Workflow | Priority | TAM |
|---|---------|----------|----------|-----|
| 1 | Universal Financial Data Extraction Engine | WF-005 | Month 1–2 | $1.2B |
| 2 | CRE Underwriting Accelerator | WF-004 | Month 2–4 | $1.8B |
| 3 | Project Finance Modeling Platform | WF-002 | Month 4–6 | $800M+ |
| 4 | CIM Generation Engine | WF-003 | Post-launch (Month 7+) | $2.5B |
| 5 | M&A Due Diligence Pipeline | WF-001 | Post-launch (Month 9+) | $4.1B |

**6-Month Target: Products 1–3 ($3.8B TAM) | Combined TAM: $10.4B+**

---

## 📐 Data Schemas

### Input: Financial Document Upload
```json
{
  "document_id": "uuid",
  "uploaded_by": "user_id",
  "organization_id": "org_id",
  "filename": "string",
  "file_type": "pdf | docx | xlsx | csv | image",
  "file_size_bytes": "number",
  "upload_timestamp": "ISO8601",
  "document_type": "10-K | 10-Q | annual_report | rent_roll | offering_memorandum | term_sheet | contract | financial_statement | other",
  "metadata": {
    "company_name": "string | null",
    "fiscal_period": "string | null",
    "currency": "string | null",
    "language": "string"
  }
}
```

### Output: Extracted Financial Data
```json
{
  "extraction_id": "uuid",
  "document_id": "uuid",
  "extraction_timestamp": "ISO8601",
  "document_type_detected": "string",
  "quality_score": "number (0-100)",
  "statements": {
    "income_statement": {
      "periods": ["FY2023", "FY2024"],
      "line_items": [
        {
          "label": "Revenue",
          "standardized_label": "total_revenue",
          "values": { "FY2023": 1000000, "FY2024": 1200000 },
          "currency": "USD",
          "confidence": 0.97,
          "source_page": 45,
          "source_coordinates": { "x": 100, "y": 200, "w": 300, "h": 20 }
        }
      ]
    },
    "balance_sheet": {},
    "cash_flow_statement": {}
  },
  "calculated_metrics": {
    "gross_margin": { "FY2023": 0.45, "FY2024": 0.48 },
    "ebitda_margin": { "FY2023": 0.22, "FY2024": 0.25 },
    "current_ratio": { "FY2023": 1.5, "FY2024": 1.8 },
    "debt_to_equity": { "FY2023": 0.6, "FY2024": 0.5 }
  },
  "validation": {
    "balance_sheet_balanced": true,
    "cash_flow_reconciled": true,
    "cross_statement_consistent": true,
    "items_flagged_for_review": 3
  }
}
```

### Output: CRE Pro Forma
```json
{
  "property_id": "uuid",
  "property_type": "multifamily | office | retail | industrial | mixed_use",
  "property_details": {
    "address": "string",
    "year_built": "number",
    "total_sf": "number",
    "unit_count": "number"
  },
  "rent_roll": [
    {
      "tenant": "string",
      "suite": "string",
      "sf": "number",
      "monthly_rent": "number",
      "annual_rent": "number",
      "lease_start": "date",
      "lease_end": "date",
      "escalation_rate": "number"
    }
  ],
  "pro_forma": {
    "hold_period_years": 5,
    "annual_projections": [
      {
        "year": 1,
        "gross_potential_rent": "number",
        "vacancy_loss": "number",
        "effective_gross_income": "number",
        "operating_expenses": "number",
        "net_operating_income": "number",
        "debt_service": "number",
        "cash_flow_before_tax": "number"
      }
    ]
  },
  "returns": {
    "unleveraged_irr": "number",
    "leveraged_irr": "number",
    "equity_multiple": "number",
    "cash_on_cash_return": "number",
    "going_in_cap_rate": "number",
    "exit_cap_rate": "number"
  }
}
```

---

## 🛡️ Behavioral Rules (Immutable)

### Security
1. **NEVER** store raw API credentials in code or database
2. **NEVER** transmit financial documents without encryption (TLS in transit, AES-256 at rest)
3. **NEVER** expose raw financial data in client-side code
4. **ALWAYS** maintain audit trails for every data access and modification
5. **ALWAYS** enforce role-based access control (RBAC)

### Data Integrity
6. **NEVER** present AI-extracted data as verified without confidence scores
7. **ALWAYS** flag low-confidence extractions for human review (< 95% confidence)
8. **NEVER** auto-approve financial figures without cross-validation
9. **ALWAYS** maintain source attribution for every extracted data point
10. **ALWAYS** preserve original documents immutably

### AI Behavior
11. **NEVER** hallucinate financial figures — use only extracted/verified data
12. **ALWAYS** use deterministic tools for calculations (Python scripts, not LLM)
13. **NEVER** make investment recommendations or provide financial advice
14. **ALWAYS** include disclaimers on AI-generated content
15. LLMs handle NLP tasks ONLY; business logic is deterministic code

### Compliance
16. SOC 2 Type II compliance target
17. GDPR compliance for European clients
18. Data residency requirements per jurisdiction
19. Regular security audits and penetration testing

### Tone & Communication
20. Professional, institutional-grade language in all reports
21. Technical precision in financial terminology
22. No casual or ambiguous language in generated documents
23. Match industry conventions (IB-speak, CRE terminology, PF jargon)

---

## 🏗️ Architectural Invariants

### Technology Stack
| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15 (App Router) + TypeScript |
| **UI Design Tool** | Google Stitch (AI-generated UI → React/HTML export) |
| **Styling** | Tailwind CSS (Stitch default export) + design system tokens |
| **Backend API** | Next.js API Routes (orchestration) + Python FastAPI (AI core) |
| **LLM** | Anthropic Claude Opus 4.6 (sole provider) |
| **Database** | PostgreSQL 16+ (Supabase/Neon) |
| **Vector Store** | pgvector |
| **Cache** | Redis |
| **Object Storage** | Google Cloud Storage |
| **Hosting** | Google Cloud Run (₹26K GCP trial credit) |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker |

### A.N.T. 3-Layer Architecture
- **Layer 1 — Architecture** (`architecture/`): Markdown SOPs defining goals, inputs, tool logic, edge cases
- **Layer 2 — Navigation**: AI reasoning layer that routes data between SOPs and Tools
- **Layer 3 — Tools** (`tools/`): Deterministic Python scripts, atomic and testable

### Frontend Design Workflow (Google Stitch)
1. Define screen requirements (descriptions + sketches)
2. Generate UI in Google Stitch (stitch.withgoogle.com)
3. Export as React components / HTML + Tailwind CSS
4. Integrate into Next.js app, wire to FastAPI backend
5. Polish interactions, add real data bindings

### File Structure
```
Finance AI SaaS/
├── gemini.md                    # THIS FILE — Project Constitution
├── task_plan.md                 # Phase tracking
├── findings.md                  # Research log
├── progress.md                  # Activity log
├── .env                         # API keys/secrets
├── architecture/                # Layer 1: SOPs
├── tools/                       # Layer 3: Python scripts
├── .tmp/                        # Temporary workbench
├── frontend/                    # Next.js application
├── backend/                     # Python FastAPI service
├── Planning/                    # Planning documents
└── docker-compose.yml           # Local dev stack
```

### The Golden Rule
> If logic changes, update the SOP in `architecture/` **before** updating the code in `tools/`.

---

## 🔧 Self-Annealing Protocol

When a tool fails or an error occurs:
1. **Analyze**: Read the stack trace and error message. Do not guess.
2. **Patch**: Fix the Python script in `tools/`.
3. **Test**: Verify the fix works.
4. **Update Architecture**: Update the corresponding `.md` in `architecture/` with the learning.

---

## 📋 Maintenance Log

| Date | Change | Author |
|------|--------|--------|
| 2026-02-12 | Initial constitution created. Protocol 0 initialized. | System Pilot |
| 2026-02-12 | LLM changed from Gemini to Claude Opus 4.6 per user preference. | System Pilot |
| 2026-02-12 | OpenAI removed entirely — Claude Opus 4.6 sole LLM. | System Pilot |
| 2026-02-12 | Added Google Stitch for frontend. Timeline compressed to 6 months (Products 1–3). GCP ₹26K credit noted. | System Pilot |
