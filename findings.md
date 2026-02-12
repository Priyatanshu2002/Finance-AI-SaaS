# Finance AI SaaS — Findings (`findings.md`)
> Research discoveries, constraints, and learnings. Updated continuously.

---

## 2026-02-12: Initial Research

### Market Research
- **Combined TAM**: $10.4B+ across 5 products
- **Strategic Insight**: Product 1 (Data Extraction, WF-005) is the infrastructure layer powering Products 2–5. Build-first advantage.
- **Greenfield Opportunity**: Project Finance Modeling has zero dominant SaaS player — $800M+ underserved market.
- **Highest Value Target**: M&A Due Diligence at $4.1B TAM, $250K–$1M/year enterprise deals.

### Competitive Gaps Identified
| Product | Key Gap in Market |
|---------|-------------------|
| Data Extraction | No tool covers private companies + any format |
| CRE Underwriting | Nobody does AI rent-roll extraction + auto pro forma together |
| Project Finance | No SaaS competitor exists at all |
| CIM Generation | Existing tools are narrow or not AI-native |
| Due Diligence | No one owns the full DD workflow end-to-end |

### Technology Findings

#### Open-Source Tools (Validated)
| Tool | Purpose | Status |
|------|---------|--------|
| **MinerU** (opendatalab) | PDF → markdown/JSON, table → HTML, OCR for 109 languages | Active 2024–2025 |
| **PDF-Extract-Kit** (opendatalab) | Layout detection, table extraction from financial PDFs | Active 2024–2025 |
| **Tabula** | Table extraction from structured PDFs | Mature, stable |
| **Camelot** | Advanced table extraction with customization | Mature, stable |
| **pdfplumber** | Clean PDF text/table extraction | Active |
| **FinGPT** (AI4Finance) | Financial LLM, fine-tunable with new data | Active |
| **OpenBB Platform** | Financial analysis, 100+ data providers | Active |
| **QuantLib-Python** | Derivatives, fixed income, risk management | Mature |
| **microsoft/table-transformer** | Deep learning table detection (TATR) | Active |
| **parsee-ai/parsee-pdf-reader** | Financial table extraction with numeric preservation | Active |

#### LLM Decision: Claude Opus 4.6 (Sole Provider)
- **Reason**: User confirmed Claude has proven financial modeling capability
- **Provider**: Anthropic API (no OpenAI — user explicitly excluded)
- **Use Cases**: Content generation (CIM narratives, DD summaries), NLP tasks (NER, classification, summarization), document understanding
- **NOT used for**: Calculations, financial logic, business rules (these are deterministic Python)

#### Tech Stack Constraints
- NotebookLM does not support `.json` file uploads (only `.csv`, `.docx`, `.md`, `.pdf`, `.txt`, etc.)
- Project finance debt sculpting has no dedicated open-source Python library — must build custom using NumPy/Pandas + circular reference solvers
- Edward Bodmer's methodology (edbodmer.com) is the reference for programmatic debt sculpting

### Infrastructure Notes
- **Supabase vs Neon**: Both viable for managed PostgreSQL. Supabase includes Auth + Realtime out of the box.
- **pgvector**: Enables semantic search directly in PostgreSQL — avoids separate vector DB cost.
- **Cloud Run**: Serverless containers scale to zero — ideal for early-stage cost management.
- **GCP Trial Credit**: User has ₹26,000 (~$310 USD) — enough for 3–6 months of Cloud Run + Cloud Vision + Storage.

### Frontend Design — Google Stitch
- **What**: AI-powered UI design tool by Google Labs (launched Google I/O 2025)
- **Built on**: Gemini 2.5 Pro / Flash models
- **Input**: Text prompts or sketches/screenshots
- **Output**: React components, HTML + Tailwind CSS, Figma layers
- **Cost**: Free (experimental)
- **Impact**: Cuts frontend development time by ~50% per product
- **Workflow**: Describe screen → Stitch generates UI → Export React → Integrate into Next.js → Wire to API
- **Note**: Stitch exports Tailwind CSS by default — styling changed from vanilla CSS to Tailwind

### Timeline Decision
- **Original**: 18 months for all 5 products
- **Compressed**: 6 months for Products 1–3 ($3.8B TAM)
- **Rationale**: Knowledge base acceleration + Stitch frontend automation
- **Products 4–5**: Deferred to post-launch (Month 7+)
