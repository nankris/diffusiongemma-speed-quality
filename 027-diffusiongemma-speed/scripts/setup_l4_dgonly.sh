#!/bin/bash
# #027 run-2 rerun setup on a Colab L4: build llama.cpp DiffusionGemma PR (#24423) with CUDA (sm_89), download the DiffusionGemma Q4_K_M GGUF in parallel.
set -x
LOG=/content/r027; mkdir -p $LOG
cd /content
( pip install -q -U "huggingface_hub[cli]" hf_transfer >/dev/null 2>&1
  hf download unsloth/diffusiongemma-26B-A4B-it-GGUF --include "*Q4_K_M*" --local-dir /content/m/dg > $LOG/dl_dg.log 2>&1; echo "DG_DL_DONE $?" >> $LOG/status ) &
git clone -q https://github.com/ggml-org/llama.cpp > $LOG/build.log 2>&1
cd llama.cpp
git fetch -q origin pull/24423/head:diffusiongemma >> $LOG/build.log 2>&1 && git checkout -q diffusiongemma >> $LOG/build.log 2>&1
git log -1 --format="%H %cd %s" > $LOG/commit.txt
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 -DLLAMA_CURL=OFF >> $LOG/build.log 2>&1
cmake --build build -j$(nproc) --config Release --target llama-diffusion-cli >> $LOG/build.log 2>&1
echo "BUILD_DONE $?" >> $LOG/status
wait
echo "ALL_SETUP_DONE" >> $LOG/status
