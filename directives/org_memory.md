# Directive: Organizational Memory

**Goal:** Allow users to input their baseline organizational details (Mission, Programs, Outcomes, Stats), and accurately store it on the filesystem so subsequent AI interactions can use it as a grounding context.

**Inputs:**
- Mission text (free text)
- Programs description (free text)
- Outcomes history (free text)
- Core stats (free text)

**Tools/Scripts to use:**
- `execution/save_org_data.py` - validates and saves the JSON to `data/org_memory.json`

**Outputs:**
- A persistent `org_memory.json` file in the `/data` directory.
- A success or error response returned to the user via the UI.

**Edge Cases to watch for:**
- User enters blank values (App should handle missing keys gracefully but allow them)
- File directory missing (Script must auto-create `/data` if it doesn't exist)
