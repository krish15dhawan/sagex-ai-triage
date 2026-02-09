import requests

def ask_llama(prompt: str, model: str = "llama3.1:8b") -> str:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=180
    )
    r.raise_for_status()
    return r.json()["response"].strip()
