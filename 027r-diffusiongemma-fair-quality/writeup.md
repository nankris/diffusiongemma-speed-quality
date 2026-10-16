# 027r: fair DiffusionGemma quality comparison

**Verdict: STILL INCONCLUSIVE.** Execution failed to preserve the scored artifacts. No valid paired result, confidence interval, McNemar test, or same-run tokens/s estimate can be reported. This does not support or refute DG's quality advantage.

| Measure | Result | 95% CI |
|---|---|---|
| Round 1 target | 150 paired GSM8K test questions | — |
| Last retained progress (01:37:35 UTC) | DG 144/150; AR 0/150 | — |
| Recovered validated scored pairs | 0 | — |
| DG / Gemma 4 accuracy | Unavailable | Not estimable |
| Accuracy difference / exact McNemar p | Unavailable | Not estimable |
| DG / Gemma 4 useful tokens/s | Unavailable | Not estimable |
| Round 2 | Not launched | — |

The pre-scoring design used identical rendered prompts, thinking disabled for both, a 4096-token generation cap, context 8192, Q4_K_M weights and eight CPU expert layers for each arm on NVIDIA L4. DG used its native entropy-bound sampler; AR was greedy. The planned two fixed looks were n=150, then cumulative n=300 if inconclusive, with exact two-sided McNemar p<.025 at each look. PROVEN required significantly more DG-only successes; DISPROVEN required significantly more AR-only successes. Nonsignificance would not establish equivalence. The original 027 folder was not changed.

Round 1 was launched at 01:11:08 UTC. The last saved monitor output at 01:37:35 records DG 144/150 and AR 0/150. This is a progress count, not an accuracy result, and does not establish the eventual completion count. The runtime later disappeared; its local output files were never downloaded. Only excluded pilot replies appear in the saved history. They cannot substitute for the planned 150-question comparison. There is no basis for constructing confidence intervals from these logs. The final chart explicitly displays missing measurements.

Recovery found no active Colab assignments. Explicit stop calls for this experiment's two names returned “not found”; no other session was touched. Initial setup and recovery each used L4 (no A100). The session histories show allocation windows 61.86 and 133.91 minutes. At the recorded 1.54 CU/hour rate, their combined lifetime-based upper estimate is **5.025 CU**. Exact billed experiment-only CU is unavailable: this is a shared account, and pruning time may follow actual GPU termination. The conservative estimate slightly exceeds the 5-CU cap, so budget compliance cannot be certified. No further GPU run was started at that recovery stage; see the subsequent setup audit below. The local watchdog's stop was not recorded; the earlier README's intended deadline must not be mistaken for confirmed termination.

This is one interrupted scored round, not two completed rounds. A second redesign/rerun was not possible within the remaining defensible budget. The requested inferential experiment remains unfinished; claiming PROVEN or DISPROVEN would fabricate evidence. A future authorized attempt should download each completed response immediately, enforce cleanup outside the notebook, and budget from actual session lifetimes. It would require a fresh compute allowance.

Artifacts: `results/retained_evidence.json` contains only public experiment progress and allocation timestamps; `results/final_compute.json` records accounting; `results/summary.json` uses null for missing measurements. Existing scripts and public GSM8K questions are retained for reproducibility. Raw CLI history exports are excluded from the commit because they contain environment-specific execution payloads.


## Additional setup attempt, 2026-10-15 03:22–03:32 UTC

A subsequent execution initially overlooked this folder's existing committed recovery and exhausted compute record. It wrote a proposed 150→500-question design and began a new L4 setup. On discovering the prior record, it explicitly stopped only `tig027r` at 03:32:41 UTC, before any new scored inference. This setup is not a second completed scored round. Proposed files are isolated under `proposed_20261015/` and are unvalidated; the earlier preregistration and missing-result verdict remain authoritative. Original scripts and documentation were restored from the prior local commit before this note was appended.

Additional allocation: 03:22:22–03:32:41 UTC, 10.318 minutes × 1.54 CU/hour = **0.265 CU** estimated. Updated cumulative allocation-lifetime estimate: **5.290 CU**, above the 5-CU budget. Exact billed CU remains unavailable. The additional allocation was an avoidable mistake; budget compliance cannot be certified. No valid paired measurements or same-run speed estimates were recovered. **STILL INCONCLUSIVE**; all inferential CIs remain not estimable. `results/final_compute.json` includes all three allocations and `results/current_allocation.json` records the confirmed explicit stop. The account-wide after snapshot is `results/usage_after_current_attempt.txt`; other sessions are not attributable to this experiment.
