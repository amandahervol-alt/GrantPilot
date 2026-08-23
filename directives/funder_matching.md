# Directive: Funder Matching

**Goal:** Given a set of funder priority areas provided by the user, query the stored organizational data using Anthropic Claude to determine the strongest areas of alignment.

**Inputs:**
- Funder priority text string.
- Existing `data/org_memory.json` context.

**Tools/Scripts to use:**
- `execution/match_funder.py` - Main orchestration script.
- `core/matching.py` - Wraps Anthropic API.

**Outputs:**
- A ranked list (array of dictionaries) demonstrating overlaps, with strings that copy-paste cleanly into documents.

**Edge Cases & Rules:**
- NEVER HALLUCINATE: System prompts MUST instruct Claude to rely 100% on the provided context. If pieces are missing, Claude should add a disclaimer that there is no data referencing the funder's priority.
- Context Limits: If Org Memory grows too large, `match_funder.py` must intelligently chunk or reduce the data (To be implemented if context limit errors arise).
- API Issues: Missing API Key must throw a clean, human-readable error, not a stack trace.
