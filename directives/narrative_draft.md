# Directive: Narrative Draft Generation

**Goal:** Generate high-quality, grant-ready narrative sections tailored to a specific grant component (e.g. Statement of Need, Program Description, Evaluation & Metrics, Executive Summary) grounded strictly in matched organizational data and document excerpts.

**Inputs:**
- Matched content excerpts (or combined org memory + document index).
- Funder priority context.
- Section type (e.g. `Executive Summary`, `Statement of Need`, `Program Design / Methodology`, `Outcomes & Evaluation`, `Budget Narrative`).
- Target word count (e.g. 250, 500, 750 words).

**Tools/Scripts to use:**
- `execution/generate_narrative.py` - Main orchestration script.
- `core/narrative.py` - Wraps Anthropic API with strict anti-hallucination prompt templates.

**Outputs:**
- A clean, cohesive markdown/text draft formatted and ready for copy-pasting into grant portals.
- List of any detected data gaps or information that was unavailable in the source data.

**Edge Cases & Rules:**
- NEVER HALLUCINATE: Claude must only draw from the provided matched org data and documents. Never invent metrics, dates, partner names, or program outcomes.
- Flag Gaps: If the prompt asks for details missing from the org memory (e.g., specific demographic data or partner letters), insert bracketed callouts: `[GAP: Missing demographic breakdown for Target Region]`.
- Word Count Adherence: Maintain +/- 10% of the requested target word count without trailing off abruptly.
- Error Handling: Return user-friendly error messages if API keys are missing or rate limits occur.
