#!/bin/bash
# retry helper: try to allocate tig027b on L4 and launch the DG rerun; prints result
source /workspace/tools/setup.sh >/dev/null 2>&1; export PATH=/workspace/tools/bin:$PATH
cd /workspace/work/tig/027-diffusiongemma-speed/scripts
out=$(timeout 100 colab new -s tig027b --gpu L4 2>&1 | tail -1); echo "$out"
if echo "$out" | grep -q READY; then
  date -u +%s > ../results/session2_start_epoch
  for f in setup_l4_dgonly.sh bench_run2_dg.sh prompts_run2.json; do colab upload -s tig027b $f /content/$f 2>&1|tail -1; done
  timeout 60 colab exec -s tig027b -f launch_run2_dg.py 2>&1|tail -1
fi
