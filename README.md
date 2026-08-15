# GrantPilot 🧭

**AI-Powered Grant Intelligence & Narrative Drafting Assistant for Nonprofits**

Upload your documents. Enter what your funder cares about. Get matched content and a draft narrative — instantly, grounded in your real organizational data.

---

## 🌟 What Is GrantPilot?

Grant writers spend hours hunting through scattered reports, spreadsheets, and past proposals to find the right data for each funder. **GrantPilot** solves that.

GrantPilot acts as an organizational intelligence layer — it stores what your organization has done, understands what each funder cares about, and surfaces the right narrative content instantly. Every output is grounded strictly in your real data. **No hallucinated statistics. No invented programs.**

---

## ✨ Key Features

- **Organizational Memory**: Enter and save your mission statement, programs, outcomes, impact statistics, geographic reach, and milestones. Your data persists across sessions and can be updated at any time.
- **Document Upload & Indexing**: Upload PDF, DOCX, or TXT files — past proposals, annual reports, program descriptions, anything. GrantPilot extracts and indexes the content so it's searchable during matching.
- **Funder-Focus Matching**: Enter a funder's priority areas in plain language (e.g., *"workforce development for returning citizens in rural communities"*). GrantPilot queries both your organizational memory and uploaded documents, then returns a ranked list of your most relevant content — with an explanation of why each piece fits this funder.
- **Narrative Draft Generation**: Based on matched content, GrantPilot generates a clean, copy-paste ready draft narrative section. Specify the section type (organization background, statement of need, program description) and target word count. Every sentence is grounded in your real data — gaps are flagged, not filled in.

---

## 💡 Key Design Decisions for Interview Reviewers

1. **Human-in-the-Loop Quality Gating**: Designed specifically so AI assists but never hallucinates statistics. Gaps in organizational data are explicitly flagged for human review rather than filled with probabilistic guesses.
2. **Context Window & Retrieval Optimization**: Isolates relevant narrative fragments from past proposals and annual reports before prompt construction, keeping prompt sizes compact and reducing Anthropic API latency.
3. **Structured Prompt Engine**: Enforces rigid prompt instructions to output ranked relevance scores, rationale, and structured narrative drafts suitable for federal and foundation grant standards.
4. **FastAPI & Modular Core Architecture**: Clean separation between document parsing (`core/`), API endpoints (`api/`), and frontend UI (`static/`).

---

## 🛠️ Built With

- **Backend**: Python FastAPI
- **AI**: Anthropic API (Claude 3.5 / 3.7 Sonnet)
- **Document Processing**: PyMuPDF (PDF), python-docx (DOCX)
- **Frontend**: Clean HTML/CSS/JavaScript designed for nonprofit staff

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/amandahervol-alt/GrantPilot.git
cd GrantPilot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```
*Add your `ANTHROPIC_API_KEY` to `.env`.*

### 4. Run the app
```bash
uvicorn main:app --reload
```

### 5. Open in browser
Navigate to `http://localhost:8000`.

---

## 📊 Current Status

**Version 1.0 — Core Features Complete ✅**
- [x] Organizational memory storage and retrieval
- [x] Document upload and text extraction (PDF, DOCX, TXT)
- [x] Funder-focus matching with ranked results and relevance explanations
- [x] Narrative draft generation grounded strictly in real org data
- [x] Clean, minimal UI designed for non-technical nonprofit staff

---

## 👩‍💻 About the Developer

GrantPilot was designed and built by **Amanda Hervol**, an AI Workflow Architect specializing in LLM-powered systems, workflow automation, and AI solution design for real-world operational environments. Amanda is also an experienced grant writer (~$1.76M authored in 2025, $2M+ lifetime awards) — this tool solves a problem she lives firsthand.

- 🔗 [LinkedIn](https://www.linkedin.com/in/amandaa-hervol/)
- 📧 [amandahervol@gmail.com](mailto:amandahervol@gmail.com)

---

## 🎯 Why This Matters

Nonprofit development staff are stretched thin. Writing grant proposals requires synthesizing years of program data, outcomes, and impact stories — and doing it differently for every funder's unique priorities. Most of that institutional knowledge lives in scattered documents and people's heads.

GrantPilot puts that knowledge to work. It doesn't replace the grant writer — it gives them their time back.

*Built for the people doing the work.*
