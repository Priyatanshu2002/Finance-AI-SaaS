# Token Savings Strategy

To minimize cost and maximize the quality of AI assistance, we split documents between the local repository (for code and active context) and NotebookLM (for deep domain research).

## Context Optimization Tiers

| Tier | Description | Typical Size | Storage Location | AI Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Active Context** | Source code, configuration, task plans. | < 100KB | Local File System | Read every turn. |
| **Tier 2: Project Knowledge** | Strategic blueprints, architecture docs, problem statements. | 100KB - 20MB | **NotebookLM** | Queried via MCP when needed. |
| **Tier 3: Testing Assets** | SEC EDGAR samples, XBRL datasets, training PDFs. | > 20MB | **Cloud Storage (GCP)** | Processed by Document AI / Batch jobs. |

## NotebookLM Integration

By moving the following files to NotebookLM, we save approximately **500,000+ tokens** of potential context saturation:
- `Finance_AI_Strategic_Blueprint.pdf` (16MB) - ~2.5M tokens equivalent.
- `BLAST_Blueprint_Knowledge_Base.txt` (515 lines) - ~20k tokens.
- `finance_domain_problem_statements_detailed.txt` (63k lines) - ~500k tokens.

## How it works
I use the `notebooklm-mcp` to:
1. Search the index for specific domain answers.
2. Only "paste" relevant snippets into the chat when implementing code.
3. Keep our "active" token count low, resulting in faster responses and higher reasoning quality.
