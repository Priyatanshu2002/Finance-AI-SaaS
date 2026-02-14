# Finance AI Agency — Launch Plan (`task_plan.md`)
> **Pivot:** From "SaaS Build" to "Tech-Enabled Agency" (Cash Flow First)
> **Goal:** $20k/mo MRR in 90 Days via High-Leverage Service Arbitrage

---

## Phase 1: The "CIM Factory" (Month 1) — Immediate Cash Flow

### 1.1 The "Golden" Portfolio Piece (Week 1)
- [ ] Select a past deal or public 10-K (e.g., local HVAC co) as the "Dummy Client"
- [ ] **Ingestion:** Upload docs to Claude Project to test "Thesis Extraction"
- [ ] **Drafting:** Generate a full 40-page CIM using the new modular workflow
- [ ] **Design:** Build the "Banker Style" Word Template (Masters/Styles/Colors)
- [ ] **Final Polish:** Manually review and refine to ensure "Goldman Standard" quality
- [ ] **Output:** A redacted "Sample CIM" PDF to send to prospects

### 1.2 The Sales Engine (Week 2-3)
- [ ] **Target List:** Build list of 50 Boutique Business Brokers (LinkedIn Sales Nav)
- [ ] **Offer Crafting:** "I will write your next CIM in 48 hours for $5k. Pay on delivery."
- [ ] **Outreach:** Cold email/DM campaign (aim for 5 conversations)
- [ ] **Closing:** Sign 1st Client (beta rate allowed, but get the testimonial)

### 1.3 Operations Setup (Week 4)
- [ ] Standardize the "Data Room Request List" (what we need from clients)
- [ ] Create strict "Quality Control Checklist" (prevent hallucinations)
- [ ] Set up Stripe for $5k invoicing

---

## Phase 2: The "Deal Scouting" Engine (Month 2) — Recurring Revenue

### 2.1 The Data Pipeline
- [ ] **Scraping:** Set up Firecrawl to scrape a niche (e.g., "Dental Practices in FL >$1M Rev")
- [ ] **Enrichment:** Use Opus to score leads (Succession risk, owner age, reviews)
- [ ] **Output:** Generate a "Deal Teaser" list (Excel/PDF)

### 2.2 The Retainer Pitch
- [ ] **Target:** 10 Search Funds / Boutique PE firms looking for dental roll-ups
- [ ] **Offer:** "Exclusive proprietary deal flow for $2k/mo retainer"
- [ ] **Close:** Sign 2-3 retainer clients to cover burn rate

---

## Phase 3: SaaS Infrastructure (Month 3+) — The "Back Burner"

> *Build the software in the background while the Agency makes money.*

### 3.1 Productizing the Tools
- [ ] Convert "CIM Factory" scripts into `POST /api/generate-cim`
- [ ] Convert "Deal Scout" scraper into `POST /api/find-leads`
- [ ] Build the "Client Portal" (Next.js + Stitch) for clients to self-serve

### 3.2 The Pivot to SaaS
- [ ] Once Agency MRR > $15k, stop taking new service clients
- [ ] Invite Agency clients to beta test the SaaS dashboard
- [ ] Transition from "$5k Service" to "$500/mo Subscription"

---

## Technical Tasks (Internal Tooling)
- [ ] **Extraction:** Refine `tools/ocr_extractor.py` for messy client PDFs
- [ ] **Spreading:** Build `tools/financial_spreader.py` (Excel Plugin automation)
- [ ] **Validation:** Implement `tools/validation_engine.py` to auto-flag anomalies

---

## Metrics for Success
- [ ] **Month 1:** 1 Portfolio CIM delivered, 1 paying client ($5k)
- [ ] **Month 2:** 3 Retainer clients ($6k MRR) + 2 CIMs ($10k) = $16k Revenue
- [ ] **Month 3:** First SaaS Beta User (converted from Agency)
