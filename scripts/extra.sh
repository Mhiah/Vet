#!/usr/bin/env bash
# Extra experiments, run by the "Extra experiments" workflow from the crux/ checkout.
# Edit this file and change the EXTRA file to start a run.
set -uo pipefail

echo "== Models this SERV key can use =="
curl -sS -m 30 "${SERV_BASE_URL:-https://inference-api.openserv.ai/v1}/models" -H "Authorization: Bearer $SERV_API_KEY" \
  | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{const j=JSON.parse(s);const ids=(j.data||j.models||[]).map(m=>m.id||m.name||m);console.log(ids.join("\n"));require("fs").writeFileSync(process.env.VET_ROOT+"/results/serv_models.txt",ids.join("\n")+"\n")}catch(e){console.log("could not list models:",s.slice(0,300))}})'

echo "== Control question: full run, then three repeats =="
VET_SET=controls npx tsx ../scripts/run.ts
VET_SET=controls npx tsx ../scripts/replicate.ts 3

echo "== Fix variants on saved first-run records =="
npx tsx ../scripts/variants.ts 2
