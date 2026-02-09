import json
from app.ollama_ai import ask_llama

def _extract_json_array(text: str):
    a = text.find("[")
    b = text.rfind("]")
    if a == -1 or b == -1 or b < a:
        raise ValueError("No JSON array found. Model output:\n" + text)
    return json.loads(text[a:b+1])

def extract_requests(doc_text: str) -> list[dict]:
    prompt = f"""
You are a strict JSON generator.

You MUST output ONLY valid JSON.
No words, no markdown, no explanations.

Return a JSON array of change requests found in the document.
Each array item MUST have EXACTLY these keys:
- title (string)
- summary (string)
- type (one of: bug, feature, change, question)
- priority (one of: low, medium, high)
- affected_area (array of strings; each must be one of: frontend, backend, billing, auth, ai)
- confidence (number from 0 to 1)

DOCUMENT:
{doc_text}

JSON:
""".strip()

    raw = ask_llama(prompt)
    data = _extract_json_array(raw)

    # Minimal cleanup to enforce types
    cleaned = []
    for t in data:
        cleaned.append({
            "title": str(t.get("title", "")),
            "summary": str(t.get("summary", "")),
            "type": str(t.get("type", "feature")),
            "priority": str(t.get("priority", "medium")),
            "affected_area": t.get("affected_area", ["backend"]) if isinstance(t.get("affected_area", ["backend"]), list) else ["backend"],
            "confidence": float(t.get("confidence", 0.5)),
        })
    return cleaned
