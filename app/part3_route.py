import json
from app.ollama_ai import ask_llama

def route_one(ticket: dict) -> dict:
    prompt = f"""
Return ONLY JSON: {{"team":"Engineering|Product|Support|Security","why":"one sentence"}}

Rules:
- Security: API keys, vulnerabilities, data exposure, audit logs, credentials
- Support: how-to questions, usage questions
- Engineering: bugs, crashes, performance issues
- Product: feature requests, changes, improvements

TICKET:
{json.dumps(ticket)}
JSON:
""".strip()

    raw = ask_llama(prompt)
    a = raw.find("{")
    b = raw.rfind("}")
    if a == -1 or b == -1 or b < a:
        return {"team":"Product","why":"Fallback: model output was not valid JSON."}

    return json.loads(raw[a:b+1])
