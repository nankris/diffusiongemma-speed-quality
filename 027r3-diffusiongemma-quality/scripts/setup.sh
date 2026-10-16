#!/bin/bash
set -euo pipefail
mkdir -p /content/current
cd /content
python -m pip install -q 'huggingface_hub[cli]' tokenizers
(
hf download unsloth/diffusiongemma-26B-A4B-it-GGUF --include '*Q4_K_M*' --local-dir /content/m/dg > /content/current/download_dg.log 2>&1
hf download unsloth/gemma-4-26B-A4B-it-GGUF --include 'gemma-4-26B-A4B-it-UD-Q4_K_M.gguf' --local-dir /content/m/g4 > /content/current/download_ar.log 2>&1
) &
dl_pid=$!
mkdir -p llama.cpp
cd llama.cpp
git init -q
git remote add origin https://github.com/ggml-org/llama.cpp
git fetch -q --depth 1 origin 6a7388aac74ab896d9d4f0fb187ddac4847c02f0
git checkout -q 6a7388aac74ab896d9d4f0fb187ddac4847c02f0
git rev-parse HEAD > /content/current/source_commit.txt
python /content/patch.py
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 -DLLAMA_CURL=OFF
cmake --build build -j4 --target llama-diffusion-cli llama-server
wait "$dl_pid"
python - <<'META'
from pathlib import Path
import json
rows=[]
for arm in ['dg','g4']:
 for f in Path('/content/m/'+arm).rglob('*.gguf'):
  rows.append(dict(arm=arm,name=f.name,bytes=f.stat().st_size))
 for f in Path('/content/m/'+arm+'/.cache/huggingface/download').rglob('*.metadata'):
  rows.append(dict(arm=arm,metadata_name=f.name,metadata=f.read_text()))
Path('/content/current/model_manifest.json').write_text(json.dumps(rows,indent=2))
META
touch /content/current/SETUP_DONE
