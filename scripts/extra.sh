#!/usr/bin/env bash
# Extra experiments, run by the "Extra experiments" workflow from the crux/ checkout.
# Edit this file and change the EXTRA file to start a run.
#
# Already run and saved (kept here as a record of what was executed):
#   VET_SET=controls npx tsx ../scripts/run.ts            -> results/controls/
#   VET_SET=controls npx tsx ../scripts/replicate.ts 3    -> results/controls/replicates/
#   npx tsx ../scripts/variants.ts 2                      -> results/variants/
set -uo pipefail

echo "== Second and third model: one pass of the reasoning on the saved evidence (no searches) =="
for MODEL in claude-haiku-4.5 gemma-4-31b-it; do
  echo "-- $MODEL --"
  SERV_MODEL="$MODEL" VET_OUT="model-$MODEL" npx tsx ../scripts/replicate.ts 1
done
