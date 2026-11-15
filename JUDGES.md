# Guide for judges

This page is for anyone assessing Vet. It says what the entry claims, where each claim can be checked, and where the weak points are, so you do not have to hunt for any of it.

## In one minute

**Question.** When an AI system is made to argue against its own answer before giving advice, is the advice more honest?

**Design.** One model answers nine business questions three ways: a plain prompt, one prompt over web evidence, and a pipeline that stress-tests its own answer. The last two see identical evidence. Questions are grouped by how much evidence exists (well-evidenced, contested, thin).

**Finding.** The stress-tested briefs scored highest on a rubric fixed in advance. But the stress test judged the first answer "weakened" in 49 of 49 runs, confidence never rose, and with the main model every final answer was labelled "medium". The system's confidence followed the evidence before the stress test and not after it. The rubric rewarded this, because a brief that says "medium" reads as honest every time. Two fixes were tried and failed.

**Why it matters.** Self-critique steps are spreading in AI products because their output looks careful. This is evidence that a step can improve the wording of advice while removing the information in its confidence, and that scoring briefs one at a time will not catch it.

## Where everything is

| You want | Go to |
| --- | --- |
| The report | [`report/Vet-report.pdf`](report/Vet-report.pdf) (main text ends on page 8) |
| The plain-language summary | [`README.md`](README.md) |
| The rubric | [`rubric.md`](rubric.md) |
| The questions | [`questions.json`](questions.json), [`controls.json`](controls.json) |
| The raw runs | [`results/`](results), explained in [`results/README.md`](results/README.md) |
| The briefs as the scorers saw them | [`analysis/blinded_briefs.md`](analysis/blinded_briefs.md) |
| Both sets of marks | [`analysis/scores.json`](analysis/scores.json), [`analysis/scores_second.json`](analysis/scores_second.json) |
| Every computed number | [`analysis/summary.json`](analysis/summary.json), [`analysis/checks.json`](analysis/checks.json) |
| The code that ran the study | [`scripts/`](scripts) |

## How the entry meets the judging criteria

**Impact and novelty**
- It tests a design pattern that is in wide use (self-critique before answering) on the property the pattern is meant to improve.
- It reports a result that cuts against the pattern, and against the author's own tool.
- It shows a specific way a decision-brief rubric can mislead: a criterion about honest confidence gave 4.3 to briefs labelled medium and 2.6 to briefs labelled high, so a method that always says medium wins.
- It includes a negative result: two natural fixes did not work.

**Execution quality**
- The stress-tested and one-shot methods get identical evidence, so the stress test is the only difference between them.
- One measure needs no judgement at all: the confidence labels are read from the output.
- The rubric was committed before any brief existed (see the commit history: the rubric is in the first commit, the first run comes after).
- Each question was run four times. A control question, a second model and a second scorer were added.
- Only exact tests are used, which suit nine questions, and they are labelled as added after the fact.
- All code, every run record and both sets of marks are public.

**Clarity**
- The report states which parts were planned and which were added after the first results.
- Limits are listed plainly in the report's appendix and in the README.
- Every number in the report is produced by a script from files in this repository.

## Check the headline numbers yourself

No API keys are needed. With Python 3 installed:

```bash
git clone https://github.com/Mhiah/Vet && cd Vet
python3 analysis/analyze.py
python3 analysis/checks.py
```

These rewrite `analysis/summary.json` and `analysis/checks.json` from the raw runs. The claims map to them like this:

| Claim in the report | Where it is computed | Field |
| --- | --- | --- |
| Final label was medium in 36 of 36 main runs | `checks.json` | `repeats.labels.final` |
| Verdict was "weakened" in 36 of 36 | `checks.json` | `repeats.verdicts` |
| First answer: 18 high, 18 medium | `checks.json` | `repeats.labels.first` |
| Mean confidence by evidence group | `checks.json` | `repeats.mean_by_group` |
| Control: high before, medium after, 4 of 4 | `checks.json` | `control` |
| Second model: 9 of 9 weakened, 3 low and 6 medium | `checks.json` | `other_models` |
| Fixes: 71 of 72 medium | `checks.json` | `fix_variants.labels` |
| Rubric means, first scorer (16.0, 21.8, 23.4) | `summary.json` | `rubric` |
| Rubric means, second scorer (15.2, 19.8, 21.8) | `checks.json` | `second_scorer.by_method` |
| Scorer agreement (all marks within one point) | `checks.json` | `second_scorer.agreement` |
| Honest-confidence mark by label (4.32 vs 2.60) | `checks.json` | `honest_confidence_score_by_label` |
| 31 of 68 challenges cite contrary evidence; 19 of 31 weakened assumptions backed | `checks.json` | `challenge_backing` |
| Direct evidence 40%, 13%, 3% | `checks.json` | `direct_claim_share.by_group` |
| Permutation and sign tests | `checks.json` | `trend_permutation_p`, `sign_tests` |

To read a single run, open any file in `results/`, for example `results/W2.json`. The three briefs are under `plain`, `one_shot` and `crux.conclusion`; the first answer is `crux.thesis`; the stress test and its verdicts are `crux.stress_test` and `crux.reevaluation`.

## What was planned, and what was added later

**Set before the first run:** the three methods, the questions and their groups, the rubric, and the expectation that a sound method is less confident where evidence is thin.

**Not predicted:** the main finding. The stress-tested label did not vary, and nobody expected that.

**Added after the first results:** the three repeats per question, the control question, the second model, the second scorer, the two fixes, the evidence check and the statistical tests. The report labels these as post hoc.

## What existed before the sprint

[Crux](https://github.com/Mhiah/crux), the research engine being tested, was written by the author before the sprint. It is used unchanged at commit `359a6f4` and none of its code is copied here. Everything in this repository was made during the sprint.

## Use of AI

An AI assistant (Claude, Anthropic) wrote the harness and analysis code, scored the briefs, and helped draft the report. The second scorer was a separate instance of the same model, given only the rubric and the unlabelled briefs. The briefs themselves were written by a different model family. The author is responsible for the content.

## The weakest points

Stated here so they are easy to weigh:

1. **Nine questions.** The repeats show stability on these questions, not generality.
2. **AI scorers only.** Two instances of one model agreed with each other. No human scored anything.
3. **The first scorer was not fully blind.** It had seen the confidence labels in the run log before scoring. The second scorer had not.
4. **The evidence groups are the author's judgement.** The check that supports them is a keyword match written after the runs.
5. **The second model had one pass,** and its pattern differed in detail from the main model's.
6. **No ground truth.** The study cannot say which confidence label was right, only that the label stopped varying with the evidence.
7. **The author built the system under test.**

The confidence-label, verdict, control, second-model and fix results do not depend on any scoring. Only the rubric tables do.

## Questions a judge might ask

**Is "medium" simply the right answer for most of these questions?**
Possibly for some. The study does not claim medium was wrong. It claims that a label which is the same for every question cannot help a reader, and that the same system gave different labels before the stress test. The control question is the clearest case: 24 supporting facts, none against, and the label still dropped from high to medium.

**Is this just one model's quirk?**
The always-medium pattern is. A second model produced low and medium labels. But it too judged the first answer weakened every time, its confidence also never rose, and its final labels did not follow the evidence.

**Could the prompt be the cause?**
The stress-tested system is told to weaken an assumption only when evidence backs the challenge, and its final step has no rule about the confidence label. An extra instruction on how to set the label was tested and changed 1 conclusion in 18.

**Does this mean self-critique is useless?**
No. Both scorers rated stress-tested briefs higher on naming the conditions that would flip the answer. The loss is in the confidence label, not the text.

**What would the author do next?**
Test whether reporting the confidence from before the stress test keeps both benefits, on a larger question set labelled by people other than the author, with human scorers and questions whose outcomes are known.
