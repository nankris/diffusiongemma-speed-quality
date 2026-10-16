#!/bin/bash
# #027 run 2, DiffusionGemma side only (rerun in a 2nd L4 session after the first attempt at -n 2048 OOMed on 24 GB:
# "GGML_ASSERT(m.sc_dev_buf != nullptr)" / cudaMalloc 256 MiB failed). Same prompts and -n 2048 as the AR run.
# EXTRA holds the memory flag chosen by the probe below.
B=/content/llama.cpp/build/bin; R=/content/r027/bench2; mkdir -p $R
DG=$(ls /content/m/dg/*.gguf); N=2048
EXTRA=""
for opt in "" "--n-cpu-moe 2" "--n-cpu-moe 4" "--n-cpu-moe 8"; do
  timeout 600 $B/llama-diffusion-cli -m $DG -ngl 99 $opt -n $N -p "Count from 1 to 5." > $R/probe.out 2> $R/probe.err
  if grep -q "total time" $R/probe.out; then EXTRA="$opt"; echo "probe ok with [$opt]" >> $R/progress_dg.txt; break; fi
  echo "probe failed with [$opt]" >> $R/progress_dg.txt
done
echo "EXTRA=[$EXTRA]" >> $R/progress_dg.txt
for id in $(python3 -c "import json;[print(p['id']) for p in json.load(open('/content/prompts_run2.json'))]"); do
  P=$(python3 -c "import json,sys;print([p['prompt'] for p in json.load(open('/content/prompts_run2.json')) if p['id']=='$id'][0])")
  s=$(date +%s.%N)
  timeout 900 $B/llama-diffusion-cli -m $DG -ngl 99 $EXTRA -n $N -p "$P" > $R/dg_${id}_r1.out 2> $R/dg_${id}_r1.err
  e=$(date +%s.%N); echo "dg $id 1 wall $(echo "$e-$s"|bc)" >> $R/walls_dg.txt
  echo "done $id" >> $R/progress_dg.txt
done
echo BENCH_DONE >> $R/progress_dg.txt
