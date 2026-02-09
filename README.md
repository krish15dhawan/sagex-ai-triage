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
This project uses a **Meta Llama-family model** (ex: Llama 3 / Llama 3.1 / another Meta checkpoint). It does **not** use GPT.

### Why Meta
- **Local control** (tickets can be processed without sending data to third-party hosted APIs)
- **Predictable cost** (local inference)
- **Fast iteration** (prompt + schema changes are easy)

### Where the model runs
This repo is designed to run the Meta model locally through one of the common runtimes:
- **Ollama** (recommended for simplicity), or
- **Transformers** (HuggingFace) if you are loading weights directly, or
- **llama.cpp / llama-cpp-python** for CPU/GGUF-style inference

> Your code chooses one of these. The setup below includes the most common option (Ollama).
> If you’re using Transformers or llama.cpp, see “Alternative runtimes” below.

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

### 5) Evidence + rationale included
**Decision:** Each ticket includes quoted evidence from the input plus a short rationale for severity/priority.
**Why:** Reviewers want to see “why did the model decide this,” not just the result.

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

> If your repo contains the literal prompt text (common), it will be in a file like `prompt.txt`, `prompts/`, or embedded in the main script.

---

## Repository structure (what each thing does)
> NOTE: I can’t reliably read your repo tree from GitHub right now, so this section is written to match the **typical structure** for this project.  
> If a filename differs, change it in **two places**:
> 1) the “Run” command
> 2) the “Files” list below

### Common folders
- `sample_docs/`
  - Input `.txt` documents used as test cases (provided below)
- `outputs/` (ignored by git)
  - JSON results produced by running the pipeline
- `.venv/` (ignored by git)
  - Local virtual environment
- `.env` (ignored by git)
  - Environment variables (model name, runtime, etc.)

### Common key files
- `run.py` (or similar)
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
