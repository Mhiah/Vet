# What is in this folder

Every file here was written by a live run. Nothing is sample data: the scripts stop if an API key is missing.

## `results/<ID>.json`: the first run, one file per question

| Field | What it holds |
| --- | --- |
| `id`, `tier`, `question` | The question and its evidence group |
| `crux_commit` | The exact version of Crux used |
| `ran_at`, `models` | When it ran and which model answered |
| `plain` | The plain brief: answer, confidence, reason, uncertainties, next steps |
| `one_shot` | The one-shot brief, same parts, plus the evidence it cites |
| `crux.research` | The search queries, the sources, and every extracted claim with its source and quoted passage |
| `crux.thesis` | The first answer, with its confidence and assumptions |
| `crux.stress_test` | Every challenge raised, its type, severity and the claims it cites |
| `crux.reevaluation` | The verdict on each assumption and on the thesis as a whole |
| `crux.conclusion` | The stress-tested brief: the final answer |
| `crux.audit` | Timing and model for each stage |

Question IDs: `W` well-evidenced, `C` contested, `T` thin evidence.

## `results/replicates/<ID>.json`: three repeats per question

The reasoning was run again on the evidence saved above, with no new searches. Each entry in `repeats` records the first answer, a summary of the stress test, the verdict, the final answer and a fresh one-shot brief.

## `results/controls/`: the obvious-answer control

`K1.json` has the same layout as a first-run file. `replicates/K1.json` holds its three repeats.

## `results/variants/<ID>.json`: the two fixes

Only the final step was re-run, from the saved first-run record. `rule` says how many assumptions the code rule reset and whether the verdict changed. Each entry in `repeats` holds four conclusions: `baseline` (unchanged), `rule`, `calibrated` (added instruction) and `both`.

## `results/model-claude-haiku-4.5/<ID>.json`: a second model

One pass of the same reasoning on the same saved evidence, in the same layout as the repeats.
