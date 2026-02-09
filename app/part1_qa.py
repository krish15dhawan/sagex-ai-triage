from app.ollama_ai import ask_llama

def chunk(text: str, size: int = 800) -> list[str]:
    text = " ".join(text.split())
    return [text[i:i+size] for i in range(0, len(text), size)]

def best_chunk(chunks: list[str], question: str) -> str:
    q = set(question.lower().split())
    best = ""
    best_score = -1
    for c in chunks:
        words = set(c.lower().split())
        score = len(q & words)
        if score > best_score:
            best_score = score
            best = c
    return best

def answer_question(doc_text: str, question: str) -> str:
    ctx = best_chunk(chunk(doc_text), question)

    prompt = f"""
Answer using ONLY the context.
If the answer is not in the context, say: I don't know.

CONTEXT:
{ctx}

QUESTION:
{question}

ANSWER:
""".strip()

    return ask_llama(prompt)
