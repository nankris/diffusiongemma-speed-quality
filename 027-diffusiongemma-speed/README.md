# #027 DiffusionGemma vs autoregressive Gemma 4: decode speed on one Colab L4

**Result:** at the same size and quantization, DiffusionGemma 26B-A4B decodes faster than Gemma 4 26B-A4B on an L4 when everything fits on the GPU: **70 vs 58 useful tok/s** (run 1). It writes about **16–17 tokens per denoising step**. Quality on our small set was the same or better. At a 2048-token limit, DiffusionGemma ran out of memory on 24 GB. It only ran after moving 2 layers' experts to the CPU (`--n-cpu-moe 2`), and that made it slower than the AR model (47 vs 57 tok/s). Even so, it finished the whole prompt set in less total time.

| | Run 1 (`-n 768`, 16 gens) | Run 2 (`-n 2048`, 28 prompts) |
|---|---|---|
| DiffusionGemma useful tok/s (median) | **70.5** | 46.9 (with `--n-cpu-moe 2`) |
| DiffusionGemma tool-reported tok/s (whole 256-tok canvas) | 82.5 | 57.2 |
| Gemma 4 26B-A4B AR tok/s (median) | 57.6 | 57.5 |
| DG tokens per denoising step (median) | 16.1 | 17.3 |
| DG in-step parallel rate (median) | ~1130 tok/s | ~690 tok/s |
| DG ms per step (mean) | 227 | 369 |
| Total generation time, all prompts (DG vs AR) | 110 s vs 142 s | 338 s vs 421 s |
| GSM8K correct (DG vs AR) | 6/8 vs 6/8 | **23/24 vs 19/24** |
| Code tests pass (DG vs AR) | **6/6 vs 4/6** | 3/3 vs 3/3 |
| Hit the token cap (DG vs AR) | 4 vs 6 | 0 vs 5 |

**Setup.** `google/diffusiongemma-26B-A4B-it` vs `gemma-4-26B-A4B-it`, both MoE with 3.8B active parameters, both Unsloth **Q4_K_M** GGUF. Built from llama.cpp PR ggml-org/llama.cpp#24423 at commit `6a7388a`. DG runs through `llama-diffusion-cli` with model defaults (entropy-bound sampler, max 48 steps per block, t 0.8→0.4, eb 0.1, 256-token canvas). AR runs through `llama-completion` (single-turn chat, temp 0). Hardware: 1× Colab L4 (24 GB). Thinking was on for both models. "Useful tok/s" counts only the reply tokens (thought + answer), using the Gemma 4 tokenizer. DG's own figure also counts the padding left in each canvas.

**Run 2 caveat.** The first DG attempt at `-n 2048` OOMed: `GGML_ASSERT(m.sc_dev_buf != nullptr)` after a 256 MiB cudaMalloc failed. Logs are in `results/bench2_dg_oom_attempt/`. The DG side was then rerun in a second L4 session. A probe there found that `--n-cpu-moe 2` was the smallest offload that fit (see `results/bench2/progress_dg.txt`). Sampler settings were the same in both runs (checked against the `diffusion_eb` log line). So the drop in in-step rate (~1150 → ~700 tok/s) and the slower run-2 DG speed come from the CPU expert offload, not from diffusion decoding. Use run 1 for the speed comparison. Run 2 still counts for quality and for total time: the AR model hit the 2048 cap 5 times while thinking, and every one of those was a GSM8K miss.

**Compute.** tig027 (setup, run 1, AR side of run 2): 50.1 min ≈ 1.29 CU. tig027b (DG rerun of run 2): 28.8 min × 1.54 CU/h ≈ 0.74 CU. **Total ≈ 2.03 CU.**

Files: `scripts/analyse.py` → `results/per_prompt.{csv,json}`, `results/summary.json`, `chart.png` · `scripts/bench*.sh`, `setup_l4*.sh`, `prompts*.json` · raw outputs in `results/bench/` (run 1) and `results/bench2/` (run 2: `ar_*` from tig027, `dg_*`/`walls_dg.txt`/`progress_dg.txt` from tig027b) · `results/feasibility.json` (the earlier T4 check: Q4_K_M at 16.8 GB doesn't fit a T4).

Sources: https://huggingface.co/google/diffusiongemma-26B-A4B-it · https://huggingface.co/unsloth/diffusiongemma-26B-A4B-it-GGUF · https://github.com/ggml-org/llama.cpp/pull/24423
