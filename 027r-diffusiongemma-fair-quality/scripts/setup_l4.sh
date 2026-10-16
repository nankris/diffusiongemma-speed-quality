#!/bin/bash
# #027 setup on a Colab L4: build llama.cpp DiffusionGemma PR (#24423) with CUDA (sm_89) and download both Q4 GGUFs in parallel.
set -x
LOG=/content/r027r; mkdir -p $LOG
cd /content
( pip install -q -U "huggingface_hub[cli]" hf_transfer >/dev/null 2>&1
  hf download unsloth/diffusiongemma-26B-A4B-it-GGUF --include "*Q4_K_M*" --local-dir /content/m/dg > $LOG/dl_dg.log 2>&1; echo "DG_DL_DONE $?" >> $LOG/status
  hf download unsloth/gemma-4-26B-A4B-it-GGUF --include "gemma-4-26B-A4B-it-UD-Q4_K_M.gguf" --local-dir /content/m/g4 > $LOG/dl_g4.log 2>&1; echo "G4_DL_DONE $?" >> $LOG/status ) &
git clone -q https://github.com/ggml-org/llama.cpp > $LOG/build.log 2>&1
cd llama.cpp
git fetch -q origin pull/24423/head:diffusiongemma >> $LOG/build.log 2>&1 && git checkout -q diffusiongemma >> $LOG/build.log 2>&1
git checkout -q 6a7388a >> $LOG/build.log 2>&1
git log -1 --format="%H %cd %s" > $LOG/commit.txt
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 -DLLAMA_CURL=OFF >> $LOG/build.log 2>&1
cmake --build build -j$(nproc) --config Release --target llama-diffusion-cli llama-cli llama-bench llama-completion >> $LOG/build.log 2>&1
echo "BUILD_DONE $?" >> $LOG/status
wait
echo "ALL_SETUP_DONE" >> $LOG/status
