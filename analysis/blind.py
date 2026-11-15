"""Render every brief in one uniform layout under a random ID, so the scorer cannot
tell from labels or formatting which method wrote it. The key is written separately."""
import json, glob, random, re, os

random.seed(20261115)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
briefs = []
# Inline claim references such as [C1, C2] or (C4-C6, C10) differ by method, so they are removed;
# the cited claims themselves are listed in full under each brief instead.
REF = re.compile(r"\s*[\[(]\s*(?:claims?\s+)?C\d+(?:\s*(?:,|-|–|and|to)\s*C?\d+)*\s*[\])]", re.I)
def strip(t):
    return REF.sub("", t)

for f in sorted(glob.glob(os.path.join(ROOT, "results", "*.json"))):
    d = json.load(open(f))
    claims = {c["id"]: c for c in d["crux"]["research"]["claims"]}
    sources = {s["id"]: s for s in d["crux"]["research"]["sources"]}

    def cite(ids):
        out = []
        for i in ids:
            c = claims.get(i)
            if not c:
                continue
            src = "; ".join(f'{sources[s].get("publisher") or "unknown"} ({sources[s]["kind"]})' for s in c["source_ids"] if s in sources)
            out.append(f'- {c["text"][:220]} [{src}]')
        return out or ["- (none cited)"]

    for method, b in (("plain", d["plain"]), ("one_shot", d["one_shot"]), ("crux", d["crux"]["conclusion"])):
        text = strip(b["final_statement"])
        lines = [
            f'QUESTION: {d["question"]}',
            f"ANSWER: {text}",
            f'CONFIDENCE: {b["confidence"]}. {strip(b["confidence_rationale"])}',
            "EVIDENCE CITED FOR:", *cite(b.get("key_supporting_claim_ids", [])),
            "EVIDENCE CITED AGAINST:", *cite(b.get("key_challenging_claim_ids", [])),
            "UNCERTAIN:", *[f"- {u}" for u in b["uncertainties"]],
            "NEXT STEPS:", *[f'- {s["step"]} (resolves: {s["resolves"]})' for s in b["next_validation_steps"]],
        ]
        briefs.append({"question": d["id"], "method": method, "text": "\n".join(lines)})

random.shuffle(briefs)
key = {}
with open(os.path.join(HERE, "blinded_briefs.md"), "w") as out:
    for n, b in enumerate(briefs, 1):
        bid = f"B{n:02d}"
        key[bid] = {"question": b["question"], "method": b["method"]}
        out.write(f"## {bid}\n\n{b['text']}\n\n")
json.dump(key, open(os.path.join(HERE, "key.json"), "w"), indent=1)
print(len(briefs), "briefs written")
