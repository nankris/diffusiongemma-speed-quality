#!/bin/bash
# #027 benchmark on Colab L4. Same prompts, same -n, both Q4_K_M GGUFs, all layers on GPU, llama.cpp PR #24423 build.
# DiffusionGemma: llama-diffusion-cli (entropy-bound sampler, model defaults: max 48 steps, t 0.8->0.4, eb 0.1).
# AR baseline: Gemma 4 26B-A4B-it (same MoE size, 3.8B active) via llama-completion in single-turn chat mode, temp 0.
B=/content/llama.cpp/build/bin; R=/content/r027/bench2; mkdir -p $R
DG=$(ls /content/m/dg/*.gguf); G4=$(ls /content/m/g4/*.gguf)
N=${N:-2048}
python3 - <<'PY' > $R/ids.txt
import json; [print(p["id"]) for p in json.load(open("/content/prompts_run2.json"))]
PY
for id in $(cat $R/ids.txt); do
  P=$(python3 -c "import json,sys;print([p['prompt'] for p in json.load(open('/content/prompts_run2.json')) if p['id']=='$id'][0])")
  for rep in 1; do
    s=$(date +%s.%N)
    timeout 900 $B/llama-diffusion-cli -m $DG -ngl 99 -n $N -p "$P" > $R/dg_${id}_r$rep.out 2> $R/dg_${id}_r$rep.err
    e=$(date +%s.%N); echo "dg $id $rep wall $(echo "$e-$s"|bc)" >> $R/walls.txt
    s=$(date +%s.%N)
    timeout 900 $B/llama-completion -m $G4 -ngl 99 -n $N -cnv -st --jinja --temp 0 -c 4096 -p "$P" < /dev/null > $R/ar_${id}_r$rep.out 2> $R/ar_${id}_r$rep.err
    e=$(date +%s.%N); echo "ar $id $rep wall $(echo "$e-$s"|bc)" >> $R/walls.txt
  done
  echo "done $id" >> $R/progress.txt
done
# pure decode speed reference for the AR model
true
echo BENCH_DONE >> $R/progress.txt
