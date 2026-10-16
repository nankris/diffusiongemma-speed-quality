# Writeup: #027 Is DiffusionGemma actually faster than normal Gemma?

**Question.** Google's DiffusionGemma writes text by denoising blocks of 256 tokens in parallel instead of producing one token at a time. Does that make it faster on one consumer-class GPU than the autoregressive Gemma 4 of the same size, and does quality hold up?

**What we compared.** DiffusionGemma 26B-A4B and Gemma 4 26B-A4B. Both are mixture-of-experts models with 3.8B active parameters, both are Unsloth Q4_K_M GGUFs, and both ran on llama.cpp PR #24423 (commit 6a7388a) on a single Colab L4 with 24 GB. They got the same prompts: GSM8K math word problems (answers checked against gold), small Python functions (checked by running unit tests), and one short explainer essay. Thinking was on for both.

**Speed, all on GPU (run 1, 768-token limit).** DiffusionGemma produced **70 useful tokens/s against 58** for Gemma 4, about 20% faster. Each denoising step settled about 16 tokens at once. Inside a step, the GPU works through the whole canvas at about 1,100 tokens/s. The entropy-bound sampler stops early once a block is confident. The tool reports 82 tok/s, but that counts the empty padding at the end of each canvas. We count only the tokens of the actual reply.

**Quality.** Run 1: GSM8K 6/8 for both, code 6/6 for DiffusionGemma vs 4/6 for Gemma 4. Run 2 (24 GSM8K, 3 code, 1 essay, 2048-token limit): GSM8K **23/24 vs 19/24**, code 3/3 for both. All five Gemma 4 misses were the model thinking until it hit the 2048-token cap without giving an answer. DiffusionGemma finished every prompt.

**The catch: memory.** At a 2048-token limit, DiffusionGemma needs a 4096-token context and big batch buffers (n_ubatch 4096). On 24 GB that OOMed. To run it, two layers' experts had to move to the CPU (`--n-cpu-moe 2`). That cut the in-step rate from ~1,150 to ~700 tok/s and per-step time rose from 227 to 369 ms, so DiffusionGemma fell to **47 tok/s vs 57**. Even then it finished the 28 prompts in 338 s against Gemma 4's 421 s, because its replies were shorter and it never ran away to the cap.

**Takeaway.** When the model and its canvas fit fully in VRAM, diffusion decoding is a real speed win at the same quality. On a 24 GB card, keep the output limit around 768–1024 tokens, or expect CPU offload to cancel the gain. Caveats: one GPU type, small prompt sets (n = 16 and 28, one sample each in run 2), an unmerged llama.cpp branch, and different reply lengths between models (we compare tokens/s and total time, not per-token cost).

**Compute used.** tig027 50.1 min ≈ 1.29 CU, tig027b 28.8 min ≈ 0.74 CU (L4 at 1.54 CU/h). Total ≈ 2.03 CU.
