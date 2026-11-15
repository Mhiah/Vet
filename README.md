# Vet

**Does an AI write a more honest decision brief when it has to attack its own answer first?**

People now ask AI systems what to do: launch this product, enter that market, change this policy. The answer usually arrives as a tidy brief with a confident recommendation. The risk is not that the brief is always wrong. It is that the brief sounds equally sure whether the evidence behind it is strong, mixed or almost absent, and the reader has no way to tell the difference.

Vet is a small study of one proposed fix: make the system form an answer, look for what would prove it wrong, and only then write the brief. It measures whether that extra step changes what the reader gets, or whether it only adds ceremony.

This is an entry for the [Apart Research AI x Epistemics sprint](https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15) (13 to 15 November 2026), Track 3: Epistemic Products.

**Read the report:** [`report/Always-Medium-report.pdf`](report/Always-Medium-report.pdf)

## What it found

Nine questions were run, three per evidence group. Two results pull in opposite directions.

**Stress-tested briefs read as more honest.** Scored blind against a rubric fixed in advance:

| Method | Score (of 25) | Flagged as overselling |
| --- | --- | --- |
| Plain | 16.0 | 2 of 9 |
| One-shot with evidence | 21.8 | 1 of 9 |
| Stress-tested | 23.4 | 0 of 9 |

**But the stress test erased the confidence signal.** The stress-tested method reported medium confidence on all nine questions and judged its own first answer "weakened" all nine times. Before the stress test, its first answer was high on the well-evidenced questions and medium on the thin-evidence ones. Afterwards the label was the same everywhere, so it tells the reader nothing about which briefs to rely on.

![The confidence label each method gave for each question](report/figure1.png)

**No method ever said "low".** Out of 36 confidence labels, 10 were high, 26 were medium and none was low, including on the questions chosen because direct evidence is scarce.

The stress test raised 68 challenges, 67 of them rated major or critical, but only 8 were contradictory evidence. The rest were weak assumptions, alternative explanations, missing evidence and risks: objections that can be raised against almost any recommendation. A critic that always wins is not informative, and a rubric that scores one brief at a time rewards the hedged wording without noticing that the label never changes.

This is a small study: nine questions, one run each, one model. It shows a pattern worth testing, not a settled effect. The report sets out the limits in full.

## The question

Take the same model and the same decision question, and produce three briefs:

| | Method | What it is |
| --- | --- | --- |
| A | **Plain** | One prompt, no web evidence. This is the ordinary chatbot answer. |
| B | **One-shot** | One prompt over a set of evidence gathered from the web. |
| C | **Stress-tested** | The same evidence, but the system first commits to an answer, attacks its own assumptions, re-judges each one, and then concludes. |

B and C are given exactly the same evidence. Any difference between them comes from the stress test and nothing else. A against B shows what evidence alone adds.

## What is measured

**1. Does confidence follow the evidence?** The questions fall into three groups (12 were written, four per group; nine were run, three per group, to fit the API budget):

- **Well-evidenced**: plenty of public data points one way.
- **Contested**: serious evidence on both sides.
- **Thin evidence**: a niche so specific that little direct evidence exists.

A sound brief should be less sure on the thin-evidence questions. A method that reports the same confidence across all three groups is overselling. This is counted straight from the recorded confidence levels, so it does not depend on anyone's judgement.

**2. Is the brief better by a fixed rubric?** Every brief is scored blind from 1 to 5 on five criteria: honest confidence, counter-evidence, traceability, cruxes, and useful next steps, plus a yes/no flag for overselling. The full rubric is in [`rubric.md`](rubric.md). It was committed before any brief was generated.

**3. What does the stress test actually do?** For the stress-tested method, the first answer and the final answer are both recorded, so the study reports how often the stress test weakened or overturned the first answer and whether the stated confidence moved with it.

## What is new here, and what existed before

The sprint rules ask for a clear line between new work and earlier work.

**Written before the sprint:** [Crux](https://github.com/Mhiah/crux), a research engine that forms a thesis, stress-tests it and records what changed. Crux is the system under test. It supplies methods B's evidence and all of method C. None of its code is copied into this repository: each run checks Crux out at one fixed commit (`359a6f4`), recorded in the workflow and in every result file.

**Written during the sprint, all in this repository:**

- the question set and its three evidence groups ([`questions.json`](questions.json))
- the harness that produces the three briefs per question ([`scripts/run.ts`](scripts/run.ts))
- the plain and one-shot comparison methods, which Crux does not have
- the scoring rubric ([`rubric.md`](rubric.md))
- the recorded runs ([`results/`](results))
- the analysis and the report

## How a run works

1. For each question, the harness asks the model for the plain brief.
2. It runs Crux on the question. Crux plans searches (about half aimed at evidence against a yes), collects sources, extracts claims and checks each quoted passage against its source, then runs thesis, stress test, re-evaluation and conclusion.
3. It gives the same extracted claims to the model in a single neutral prompt for the one-shot brief.
4. It saves everything for that question to `results/<id>.json`: the three briefs, the evidence, every intermediate stage and the Crux commit used.

The harness refuses to run on sample data. If either API key is missing it stops, so no placeholder output can end up in the results.

## Repository layout

```
questions.json         the 12 questions and their evidence groups
rubric.md              the scoring rubric, fixed before the runs
scripts/run.ts         the harness: three briefs per question
results/               one JSON file per question, written by the run
analysis/blind.py      renders the briefs under random IDs for blind scoring
analysis/scores.json   the blind scores; key.json maps IDs back to methods
analysis/analyze.py    computes every number in the report (summary.json)
analysis/figure.py     draws the figure
report/                the report (PDF and LaTeX source) and the figure
RUN                    the question IDs the last run covered
.github/workflows/     the workflow that runs the study on GitHub
```

## Running it yourself

You need Node.js 22 or newer, a [SERV Reasoning](https://docs.openserv.ai/serv-reasoning/why) key and a [Tavily](https://tavily.com) key.

```bash
git clone https://github.com/Mhiah/Vet
cd Vet
git clone https://github.com/Mhiah/crux
cd crux
git checkout 359a6f47805b97c594a59a431125730b4520e983
npm ci
export SERV_API_KEY=...
export TAVILY_API_KEY=...
npx tsx ../scripts/run.ts          # all questions
npx tsx ../scripts/run.ts W1 T2    # or only some
```

To rebuild the tables and figure from the saved runs:

```bash
python3 analysis/analyze.py
python3 analysis/figure.py
```

Questions that already have a result file are skipped, so an interrupted run can be resumed. One question costs 8 model calls and about 12 web searches.

On GitHub, the same run starts from the Actions tab (**Run the study**) once `SERV_API_KEY` and `TAVILY_API_KEY` are saved as repository secrets.

## Limits

- **Small sample.** Nine questions, one run each. The results show direction, not precise effect sizes.
- **One model, one domain.** Everything runs on one model through SERV, on business and strategy questions. Other models and other kinds of decisions may behave differently.
- **The evidence groups are the author's call.** Which questions count as well-evidenced, contested or thin was decided by judgement before the runs, not by an independent panel.
- **The rubric has no expert panel behind it.** It was written by the author, not by domain experts.
- **Scoring is done by one AI model, with imperfect blinding.** The briefs were scored once, under random IDs, by a model from a different family than the one that wrote them. Plain briefs cite no evidence, so they can be recognised, and there is no second scorer or human check. The confidence-label and stress-test results do not depend on scoring.
- **No ground truth.** The study measures whether briefs are honest about their support, not whether their recommendations turn out to be right.

## Author

Mia ([@Mhiah](https://github.com/Mhiah))
