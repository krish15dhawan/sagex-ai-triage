from pathlib import Path
import json
from app.part1_qa import answer_question
from app.part2_extract import extract_requests
from app.part3_route import route_one

DOC = "sample_docs/doc1.txt"
OUTDIR = Path("outputs")
OUTDIR.mkdir(exist_ok=True)

doc_text = Path(DOC).read_text(encoding="utf-8", errors="ignore")

print("\n=== PART 1: Q&A ===")
print(answer_question(doc_text, "What problems are mentioned?"))

print("\n=== PART 2: EXTRACT (JSON tickets) ===")
tickets = extract_requests(doc_text)
print(tickets)

print("\n=== PART 3: ROUTE + ACTION ===")
for i, t in enumerate(tickets, start=1):
    routing = route_one(t)
    ticket_id = f"TKT-{i:03d}"
    team = routing["team"]
    why = routing["why"]

    print(f"\n{ticket_id}")
    print(f"TITLE: {t['title']}")
    print(f"ROUTE TO: {team} QUEUE")
    print(f"WHY: {why}")

    payload = {"id": ticket_id, "ticket": t, "routing": routing}
    (OUTDIR / f"{ticket_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(f"\nSaved routed tickets to: {OUTDIR}/")
