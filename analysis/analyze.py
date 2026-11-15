"""Turn the recorded runs and the blind scores into the tables used in the report."""
import json, glob, os, collections, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TIERS = ["well_evidenced", "contested", "thin_evidence"]
METHODS = ["plain", "one_shot", "crux"]
LEVEL = {"low": 1, "medium": 2, "high": 3}
CRIT = ["honest_confidence", "counter_evidence", "traceability", "cruxes", "next_steps"]

runs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "results", "*.json")))]
out = {"n_questions": len(runs), "confidence": [], "by_tier": {}, "levels": {}, "stress_test": {}, "evidence": {}, "rubric": {}}

def conf(d, m):
    return d["crux"]["conclusion"]["confidence"] if m == "crux" else d[m]["confidence"]

for d in runs:
    out["confidence"].append({"id": d["id"], "tier": d["tier"], "plain": conf(d, "plain"), "one_shot": conf(d, "one_shot"),
                              "first_answer": d["crux"]["thesis"]["confidence"], "crux": conf(d, "crux"),
                              "verdict": d["crux"]["reevaluation"]["thesis_verdict"]})
for m in METHODS + ["first_answer"]:
    get = (lambda d: d["crux"]["thesis"]["confidence"]) if m == "first_answer" else (lambda d, m=m: conf(d, m))
    out["levels"][m] = dict(collections.Counter(get(d) for d in runs))
    out["by_tier"][m] = {t: round(st.mean(LEVEL[get(d)] for d in runs if d["tier"] == t), 2) for t in TIERS}

c = [d["crux"] for d in runs]
out["stress_test"] = {
    "verdicts": dict(collections.Counter(x["reevaluation"]["thesis_verdict"] for x in c)),
    "confidence_moves": dict(collections.Counter(f'{x["thesis"]["confidence"]}->{x["conclusion"]["confidence"]}' for x in c)),
    "assumption_verdicts": dict(collections.Counter(a["verdict"] for x in c for a in x["reevaluation"]["assessments"])),
    "challenges_per_run": round(st.mean(len(x["stress_test"]["challenges"]) for x in c), 1),
}
for t in TIERS:
    rs = [d["crux"]["research"] for d in runs if d["tier"] == t]
    out["evidence"][t] = {
        "claims_per_question": round(st.mean(len(r["claims"]) for r in rs), 1),
        "share_against": round(st.mean(sum(1 for x in r["claims"] if x["stance"] == "challenges") / len(r["claims"]) for r in rs), 2),
        "sources_per_question": round(st.mean(len(r["sources"]) for r in rs), 1),
    }

key = json.load(open(os.path.join(HERE, "key.json"))); scores = json.load(open(os.path.join(HERE, "scores.json")))
rows = [{"id": b, **key[b], **dict(zip(CRIT + ["oversold"], scores[b]))} for b in key]
for m in METHODS:
    r = [x for x in rows if x["method"] == m]
    out["rubric"][m] = {**{k: round(st.mean(x[k] for x in r), 2) for k in CRIT},
                        "total_of_25": round(st.mean(sum(x[k] for k in CRIT) for x in r), 1),
                        "oversold": sum(x["oversold"] for x in r), "n": len(r)}
out["rubric_rows"] = sorted(rows, key=lambda x: (x["question"], x["method"]))
json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
for k in ["levels", "by_tier", "stress_test", "evidence", "rubric"]:
    print(k, json.dumps(out[k], indent=1))
for r in out["confidence"]: print(r)
# paired comparisons crux vs one_shot on the same question
byq = collections.defaultdict(dict)
for x in rows: byq[x["question"]][x["method"]] = x
print("honest_confidence crux>one_shot:", sum(v["crux"]["honest_confidence"] > v["one_shot"]["honest_confidence"] for v in byq.values()),
      "equal:", sum(v["crux"]["honest_confidence"] == v["one_shot"]["honest_confidence"] for v in byq.values()),
      "lower:", sum(v["crux"]["honest_confidence"] < v["one_shot"]["honest_confidence"] for v in byq.values()))
print("total crux>one_shot:", sum(sum(v["crux"][k] for k in CRIT) > sum(v["one_shot"][k] for k in CRIT) for v in byq.values()),
      "equal:", sum(sum(v["crux"][k] for k in CRIT) == sum(v["one_shot"][k] for k in CRIT) for v in byq.values()))
print("blind check, method guessable from citations: plain briefs cite nothing ->", sum(1 for x in rows if x["method"]=="plain"))
