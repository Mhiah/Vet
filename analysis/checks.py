"""Robustness checks added after the first draft. Everything here is computed from files in
this repository. Checks marked POST HOC were not planned before the data were seen."""
import json, glob, os, re, itertools, collections, statistics as st
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
runs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "results", "*.json")))]
LEVEL = {"low": 1, "medium": 2, "high": 3}
RANK = {"well_evidenced": 3, "contested": 2, "thin_evidence": 1}
TIERS = list(RANK)
out = {}

# 1. Exact permutation test: is confidence higher in better-evidenced groups? (POST HOC, one-sided)
def perm_p(vals):
    tiers = [RANK[d["tier"]] for d in runs]
    obs = sum(t * v for t, v in zip(tiers, vals))
    perms = set(itertools.permutations(tiers))
    return round(sum(sum(t * v for t, v in zip(p, vals)) >= obs for p in perms) / len(perms), 4)
series = {
    "plain": [LEVEL[d["plain"]["confidence"]] for d in runs],
    "one_shot": [LEVEL[d["one_shot"]["confidence"]] for d in runs],
    "first_answer": [LEVEL[d["crux"]["thesis"]["confidence"]] for d in runs],
    "final_answer": [LEVEL[d["crux"]["conclusion"]["confidence"]] for d in runs],
}
out["trend_permutation_p"] = {k: (perm_p(v) if len(set(v)) > 1 else None) for k, v in series.items()}

# 2. Sign tests (two-sided, ties dropped)
def sign_p(pos, neg):
    n, k = pos + neg, max(pos, neg)
    return round(min(1, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n), 4) if n else None
S = json.load(open(os.path.join(HERE, "summary.json")))
CRIT = ["honest_confidence", "counter_evidence", "traceability", "cruxes", "next_steps"]
byq = collections.defaultdict(dict)
for r in S["rubric_rows"]:
    byq[r["question"]][r["method"]] = r
def diffs(keys, a="crux", b="one_shot"):
    return [sum(v[a][k] for k in keys) - sum(v[b][k] for k in keys) for v in byq.values()]
no_trace = [k for k in CRIT if k != "traceability"]
d_all, d_nt = diffs(CRIT), diffs(no_trace)
drops = [a - b for a, b in zip(series["first_answer"], series["final_answer"])]
out["sign_tests"] = {
    "rubric_total_crux_vs_one_shot": {"higher": sum(x > 0 for x in d_all), "equal": sum(x == 0 for x in d_all), "lower": sum(x < 0 for x in d_all), "p": sign_p(sum(x > 0 for x in d_all), sum(x < 0 for x in d_all))},
    "rubric_without_traceability": {"higher": sum(x > 0 for x in d_nt), "equal": sum(x == 0 for x in d_nt), "lower": sum(x < 0 for x in d_nt), "p": sign_p(sum(x > 0 for x in d_nt), sum(x < 0 for x in d_nt))},
    "confidence_first_to_final": {"fell": sum(x > 0 for x in drops), "same": sum(x == 0 for x in drops), "rose": sum(x < 0 for x in drops), "p": sign_p(sum(x > 0 for x in drops), sum(x < 0 for x in drops))},
}
out["rubric_without_traceability_of_20"] = {m: round(st.mean(sum(v[m][k] for k in no_trace) for v in byq.values()), 2) for m in ["plain", "one_shot", "crux"]}

# 3. Does the honest-confidence score simply follow the label? (POST HOC)
lab = collections.defaultdict(list)
for r in S["rubric_rows"]:
    d = next(x for x in runs if x["id"] == r["question"])
    label = d["crux"]["conclusion"]["confidence"] if r["method"] == "crux" else d[r["method"]]["confidence"]
    lab[label].append(r["honest_confidence"])
out["honest_confidence_score_by_label"] = {k: {"mean": round(st.mean(v), 2), "n": len(v)} for k, v in lab.items()}

# 4. Were the stress test's challenges backed by evidence against the answer?
n = cites_any = cites_against = 0
weakened = weakened_backed = 0
for d in runs:
    c = d["crux"]; stance = {x["id"]: x["stance"] for x in c["research"]["claims"]}
    against = lambda ch: any(stance.get(i) == "challenges" for i in ch["claim_ids"])
    for ch in c["stress_test"]["challenges"]:
        n += 1; cites_any += bool(ch["claim_ids"]); cites_against += against(ch)
    for a in c["reevaluation"]["assessments"]:
        if a["verdict"] == "weakened":
            weakened += 1
            weakened_backed += any(against(ch) for ch in c["stress_test"]["challenges"] if a["assumption_id"] in ch["target_assumption_ids"])
out["challenge_backing"] = {"challenges": n, "cite_any_claim": cites_any, "cite_a_claim_against_the_answer": cites_against,
                            "weakened_assumptions": weakened, "weakened_with_a_challenge_citing_against_evidence": weakened_backed}

# 5. Manipulation check (POST HOC): how much of the evidence is about the exact offering in the exact market?
TERMS = json.load(open(os.path.join(HERE, "directness_terms.json")))
direct = {}
for d in runs:
    a, b = TERMS[d["id"]]; claims = d["crux"]["research"]["claims"]
    direct[d["id"]] = round(sum(bool(re.search(a, c["text"].lower()) and re.search(b, c["text"].lower())) for c in claims) / len(claims), 2)
out["direct_claim_share"] = {"per_question": direct, "by_group": {t: round(st.mean(direct[d["id"]] for d in runs if d["tier"] == t), 2) for t in TIERS}}
out["evidence_volume"] = {t: {"claims": [len(d["crux"]["research"]["claims"]) for d in runs if d["tier"] == t], "sources": [len(d["crux"]["research"]["sources"]) for d in runs if d["tier"] == t]} for t in TIERS}

# 6. Repeat runs on saved evidence
reps = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "results", "replicates", "*.json")))]
if reps:
    rows = []
    for q in reps:
        orig = next(x for x in runs if x["id"] == q["id"])
        firsts = [orig["crux"]["thesis"]["confidence"]] + [r["first_answer"]["confidence"] for r in q["repeats"]]
        finals = [orig["crux"]["conclusion"]["confidence"]] + [r["final_answer"]["confidence"] for r in q["repeats"]]
        ones = [orig["one_shot"]["confidence"]] + [r["one_shot"]["confidence"] for r in q["repeats"]]
        verdicts = [orig["crux"]["reevaluation"]["thesis_verdict"]] + [r["reevaluation"]["thesis_verdict"] for r in q["repeats"]]
        rows.append({"id": q["id"], "tier": q["tier"], "first": firsts, "final": finals, "one_shot": ones, "verdicts": verdicts})
    allv = lambda k: [x for r in rows for x in r[k]]
    out["repeats"] = {
        "runs_per_question_including_first": sorted(set(len(r["final"]) for r in rows)),
        "total_pipeline_runs": len(allv("final")),
        "labels": {k: dict(collections.Counter(allv(k))) for k in ["first", "one_shot", "final"]},
        "verdicts": dict(collections.Counter(allv("verdicts"))),
        "mean_by_group": {k: {t: round(st.mean(LEVEL[x] for r in rows if r["tier"] == t for x in r[k]), 2) for t in TIERS} for k in ["first", "one_shot", "final"]},
        "questions_where_label_varied_across_runs": {k: sum(len(set(r[k])) > 1 for r in rows) for k in ["first", "one_shot", "final"]},
        "moves": dict(collections.Counter(f"{a}->{b}" for r in rows for a, b in zip(r["first"], r["final"]))),
        "rows": rows,
    }
json.dump(out, open(os.path.join(HERE, "checks.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "repeats"}, indent=1))
if reps:
    print(json.dumps({k: v for k, v in out["repeats"].items() if k != "rows"}, indent=1))
    for r in out["repeats"]["rows"]: print(r["id"], "first", r["first"], "final", r["final"], "one", r["one_shot"], r["verdicts"])
