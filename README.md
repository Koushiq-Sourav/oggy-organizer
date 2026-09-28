# Oggy Organizer

Thesis in. Confidence out.

Web AI that organizes the thesis journey: uploads thesis paper + slides,
analyzes each step, reports if appropriate for thesis/Q1 with fix list.

## Run locally
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
.venv\Scripts\python -m uvicorn src.main:app --host 127.0.0.1 --port 8001
```
Open http://127.0.0.1:8001/ (Library) and http://127.0.0.1:8001/compare

## Features
- Library: add files (auto-analyzed), X deletes from database, Finding Gaps opens the report
- Analysis: 8 checks (structure, Q1, wording, ethics, refs, academic, slides, consistency), 0-100 + Pass/Fix
- Compare: any two files (mine vs journal, v1 vs v2) - score delta, fixed/still-open/new, per-check table
- `GET /api/compare?a=<doc>&b=<doc>` - doc or report ids

## Deploy
- Vercel: import the repo, framework preset Other, it uses `api/index.py` + `vercel.json`.
  NOTE: Vercel's filesystem is ephemeral - uploads/reports reset on redeploy. For persistent
  full function use `live/render.yaml` (Render) instead.
- Rebuild CSS after style edits: `npm run tw:build`

## Structure
- src/parsers: pdf/pptx/docx/html to clean text
- src/agents: structure, q1_reviewer, word_choice, ethics, refs_checker,
  consistency, academic, slides, reporter
- src/llm: one OpenRouter gateway + prompts
- templates/ + static/: Jinja2 + Tailwind build
- tests/: pytest
- live/: run + deploy files
