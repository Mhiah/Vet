/**
 * Tests two possible fixes for the flattened confidence label, on saved first-run records.
 *
 * Each condition re-runs only Crux's conclusion stage, from the saved evidence, thesis,
 * stress test and re-evaluation. One model call per condition per question per repeat.
 *
 *   baseline    conclusion stage unchanged (shows what a conclusion-only re-run gives)
 *   rule        a code rule first edits the re-evaluation: an assumption stays "weakened" only if
 *               a challenge aimed at it cites a claim that cuts against the answer; otherwise it
 *               becomes "unresolved". If nothing is left weakened or contradicted, the thesis
 *               verdict becomes "survived". Conclusion prompt unchanged.
 *   calibrated  re-evaluation unchanged; the conclusion prompt gets one added paragraph on how to
 *               set the confidence label.
 *   both        the rule and the added paragraph together.
 *
 * Usage (from the crux/ checkout): npx tsx ../scripts/variants.ts [repeats=2] [question ids...]
 */
import { mkdir, readFile, readdir, writeFile, access } from "node:fs/promises";
import path from "node:path";
import { getProviders } from "../crux/src/lib/providers";
import { CONCLUSION_SYSTEM, formatEvidence, formatThesis, formatStressTest, formatReevaluation } from "../crux/src/lib/reasoning/prompts";
import { CONCLUSION_SCHEMA } from "../crux/src/lib/reasoning/schemas";
import type { Conclusion, Reevaluation, Research, StressTest, Thesis } from "../crux/src/lib/types";

const ROOT = process.env.VET_ROOT ?? path.resolve(process.cwd(), "..");
const DRY = process.env.VET_DRY_RUN === "1";
const IN = path.join(ROOT, DRY ? "dry-run" : "results");
const OUT = path.join(IN, "variants");

export const CALIBRATION =
  " Set the confidence label by how strong and how direct the evidence for your final answer is, not by how many objections were raised. Use high when direct evidence consistently supports the answer and the stress test produced no contrary evidence that changes it. Use low when little or no evidence bears directly on this specific decision. Things the question itself leaves open, such as the particular company or customer segment, are conditions of the answer and must not lower the confidence label.";

/** The code rule: "weakened" needs a targeting challenge that cites a claim against the answer. */
export function applyRule(research: Research, test: StressTest, reeval: Reevaluation): { reeval: Reevaluation; reset: number } {
  const stance = new Map(research.claims.map((c) => [c.id, c.stance]));
  const backed = (assumptionId: string) =>
    test.challenges.some((ch) => ch.target_assumption_ids.includes(assumptionId) && ch.claim_ids.some((id) => stance.get(id) === "challenges"));
  let reset = 0;
  const assessments = reeval.assessments.map((a) => {
    if (a.verdict !== "weakened" || backed(a.assumption_id)) return a;
    reset++;
    return { ...a, verdict: "unresolved" as const, reasoning: `${a.reasoning} [Rule applied: no challenge aimed at this assumption cites evidence against the answer, so it is unresolved, not weakened.]` };
  });
  const dented = assessments.some((a) => a.verdict === "weakened" || a.verdict === "contradicted");
  const thesis_verdict = reeval.thesis_verdict === "weakened" && !dented ? ("survived" as const) : reeval.thesis_verdict;
  return { reeval: { ...reeval, assessments, thesis_verdict }, reset };
}

const exists = (p: string) => access(p).then(() => true, () => false);

async function main() {
  const { reasoning } = getProviders();
  if (DRY === (reasoning.mode === "live")) throw new Error(DRY ? "VET_DRY_RUN is for sample data only." : "SERV_API_KEY is required: variants never run on mock data.");
  const args = process.argv.slice(2);
  const repeats = /^\d+$/.test(args[0] ?? "") ? Number(args.shift()) : 2;
  const files = (await readdir(IN)).filter((f) => f.endsWith(".json")).sort();
  await mkdir(OUT, { recursive: true });
  for (const f of files) {
    const saved = JSON.parse(await readFile(path.join(IN, f), "utf8")) as {
      id: string; tier: string; question: string;
      crux: { research: Research; thesis: Thesis; stress_test: StressTest; reevaluation: Reevaluation; conclusion: Conclusion };
    };
    if (args.length && !args.includes(saved.id)) continue;
    const file = path.join(OUT, f);
    const done: Record<string, unknown>[] = (await exists(file)) ? JSON.parse(await readFile(file, "utf8")).repeats : [];
    const { research, thesis, stress_test: test, reevaluation } = saved.crux;
    const ruled = applyRule(research, test, reevaluation);
    const conditions = [
      { name: "baseline", reeval: reevaluation, system: CONCLUSION_SYSTEM },
      { name: "rule", reeval: ruled.reeval, system: CONCLUSION_SYSTEM },
      { name: "calibrated", reeval: reevaluation, system: CONCLUSION_SYSTEM + CALIBRATION },
      { name: "both", reeval: ruled.reeval, system: CONCLUSION_SYSTEM + CALIBRATION },
    ];
    for (let r = done.length + 1; r <= repeats; r++) {
      try {
        const row: Record<string, unknown> = { repeat: r, ran_at: new Date().toISOString() };
        for (const c of conditions) {
          const res = await reasoning.reason<Conclusion>({
            step: "conclusion",
            system: c.system,
            user: [formatEvidence(saved.question, research), `Initial thesis:\n${formatThesis(thesis)}`, `Stress test:\n${formatStressTest(test)}`, `Re-evaluation:\n${formatReevaluation(c.reeval)}`].join("\n\n"),
            schema: CONCLUSION_SCHEMA,
          });
          row[c.name] = { confidence: res.output.confidence, statement: res.output.final_statement, confidence_rationale: res.output.confidence_rationale, model: res.model };
        }
        done.push(row);
        await writeFile(file, JSON.stringify({
          id: saved.id, tier: saved.tier, question: saved.question,
          first_answer: thesis.confidence, original_final: saved.crux.conclusion.confidence,
          rule: { assumptions_reset_to_unresolved: ruled.reset, verdict_before: reevaluation.thesis_verdict, verdict_after: ruled.reeval.thesis_verdict },
          repeats: done,
        }, null, 2));
        console.log(`${saved.id} repeat ${r}: ` + conditions.map((c) => `${c.name} ${(row[c.name] as { confidence: string }).confidence}`).join(", ") + ` | rule reset ${ruled.reset}, verdict ${ruled.reeval.thesis_verdict}`);
      } catch (err) {
        console.log(`${saved.id} repeat ${r} FAILED: ${err instanceof Error ? err.message : String(err)}`);
        break;
      }
    }
  }
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
