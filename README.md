# SageX AI Triage (Meta LLM) — Ticket Extraction + Prioritization to JSON

## What this is
This repo is a lightweight **AI triage system** that converts messy, unstructured issue text (customer messages, internal bug notes, feature requests) into clean, structured **JSON tickets**.

Given a folder of `.txt` documents, the pipeline:
1. Reads each document
2. Uses a **Meta Llama-family model** to:
   - identify the core problem(s)
   - classify category (auth, billing, performance, security, etc.)
   - estimate severity/priority
   - extract key evidence and impacted users
   - propose next steps / acceptance criteria
3. Writes one JSON per input file into `outputs/`

This is meant as a “first pass triage assistant” — consistent formatting, faster sorting, fewer missed security/perf issues.

---

## LLM Used (Meta, not GPT)
This project uses a **Meta Llama-family model**  Llama 3.1 . 

### Why Meta
- **Local control** (tickets can be processed without sending data to third-party hosted APIs)
- **Predictable cost** (local inference and no costs)
- **Fast iteration** (prompt + schema changes are easy)

### Where the model runs
This repo is designed to run the Meta model locally through one of the common runtimes:
- **Ollama** (recommended for simplicity), or
- **Transformers** (HuggingFace) if you are loading weights directly, or
- **llama.cpp / llama-cpp-python** for CPU/GGUF-style inference


---

## Design decisions (what + why)

### 1) Structured JSON output (strict schema)
**Decision:** Force the model to output JSON matching a predefined schema (instead of freeform text).
**Why:** Reviewers and downstream systems (Jira, Linear, Zendesk, internal dashboards) need consistent fields. JSON also makes it easy to:
- auto-filter by severity, category, priority
- route to the right team
- detect duplicates

### 2) “Security-first” triage logic
**Decision:** Any indication of credential leaks, key exposure, data exfiltration, auth bypass, etc. should automatically elevate severity/priority.
**Why:** A security issue with vague details is still often higher-risk than a well-described feature request.

### 3) Multi-issue extraction
**Decision:** A single doc may contain multiple issues (example: “SSO needed” + “dashboard slow”). The model is instructed to split into separate ticket objects or clearly separated `subissues`.
**Why:** One blob ticket kills execution. Splitting issues makes it actionable.

### 4) Deterministic-ish behavior
**Decision:** Use low temperature (or equivalent) + strict formatting rules.
**Why:** Triage should be stable across runs; creativity is not the goal.

---

## Prompting approach (exact intent)

### System intent
The model is instructed to behave as a “triage engineer” whose output must be **valid JSON only**. It is also instructed to:
- not invent facts
- only use what appears in the document
- mark unknowns explicitly (e.g., `"repro_steps": null`)

### Core extraction prompt (conceptual)
The prompt is designed around these steps:
1. Identify all distinct issues
2. For each issue:
   - summarize
   - category
   - severity + priority
   - impacted stakeholders/users
   - recommended owner/team (if your repo does that)
   - next steps / acceptance criteria
3. Output strict JSON matching schema


---

## Repository structure 

### Common folders
- `sample_docs/`
  - Input `.txt` documents used as test cases (provided below)
- `app/` 
  - Stores the question extraction and route Python files.

### Common key files
- `run.py` 
  - Main entry point: reads docs → calls model → writes JSON
- `requirements.txt`
  - Python dependencies
- `.gitignore`
  - Ensures `.venv/`, `outputs/`, `.env`, `.DS_Store` etc. are not committed

---

## How it works (high-level pipeline)
1. **Input loading**
   - The script reads every `.txt` in `sample_docs/` (or a provided folder path)
2. **Prompt assembly**
   - It wraps the doc text inside a strict instruction template
3. **Model call**
   - Calls the Meta model runtime (Ollama / Transformers / llama.cpp)
4. **Validation**
   - Ensures response is valid JSON (and optionally re-prompts if invalid)
5. **Output**
   - Writes `outputs/<doc_id>.json`

---

## Setup (Python)
### 1) Clone the repo
```bash
git clone https://github.com/krish15dhawan/sagex-ai-triage.git
cd sagex-ai-triage
