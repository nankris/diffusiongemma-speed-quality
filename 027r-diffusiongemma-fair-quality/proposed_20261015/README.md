# 027r: fair DiffusionGemma quality comparison

## Preregistered hypothesis and decision rule
Hypothesis: DiffusionGemma has higher GSM8K exact numeric answer accuracy than Gemma 4 at matched Q4_K_M quantization, identical question prompts, and thinking disabled for both. Both receive the same 4096 generated-token ceiling; cap hits are reported explicitly and invalidate a claim of a fair quality win if unequal censoring remains.

Round 1: 150 GSM8K test questions selected by seed 2701, without replacement. Round 2, only if inconclusive: expand the same sample to 500 questions. At each look use an exact two-sided McNemar test with alpha 0.025 (Bonferroni for two looks). PROVEN if significant and DG wins more discordant pairs; DISPROVEN if significant and AR wins more; otherwise STILL INCONCLUSIVE. Failure to reject is not equivalence. Report paired bootstrap 95% difference CIs (descriptive; test determines verdict), Wilson accuracy CIs, and useful output tokens/s from the same runs. No third round.

Use original llama.cpp revision and model files where obtainable, same hardware/offload policy for both arms, model-specific native chat templates with thinking disabled, and identical user message text. Record exact launch commands and raw output. Speed is descriptive and includes any architecture-specific implementation differences.

Budget: maximum 5 CU, Colab L4; stop own session on success or failure. Runtime, GPU and CU: pending.

## Implementation notes (before inference)
The original revision is available: `6a7388aac74ab896d9d4f0fb187ddac4847c02f0`.
Inspection found `common_chat_templates_inputs.enable_thinking` defaults to true and the diffusion CLI does not set it. `scripts/patch_runner.py` explicitly sets it false, and adds a batch input loop around the unchanged native generation function. Each item constructs a new single-user chat. AR uses the same revision's server, with `enable_thinking=false`, fresh prompts and cache reuse disabled. Identical user text normalizes embedded newlines to spaces for both arms. Both use `--n-cpu-moe 8` to reserve L4 memory for the 4096 budget; speed is specific to this matched offload setting. DG keeps its native stochastic entropy-bound sampler; AR uses greedy decoding, as in the original. This compares deployed default generation policies, not identical sampling algorithms.

GSM8K source: https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl ; SHA256 `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14`.
`results/questions.json` fixes the sample order and answers before inference. Explicit `Answer:` is scored first; absent that, final numeric mention is used. Accuracy CI: Wilson; paired difference CI: 20,000 seeded bootstrap samples. Speed uses a common Gemma tokenizer to count useful response tokens, excluding unused diffusion canvas padding.

Initial account balance before allocation: 179.84 CU, rate 0.00/h, 0 active assignments. Other experiments subsequently allocated sessions; account-wide balance changes cannot be attributed entirely to this run. Record session elapsed time × its L4 rate, alongside before/after account snapshots.
