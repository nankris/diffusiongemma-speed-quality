import pathlib,json,datetime,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results';PARENT=ROOT.parent
ss=json.load(open(R/'summary.json')) if (R/'summary.json').exists() else []
c=json.load(open(R/'compute.json')) if (R/'compute.json').exists() else {'gpu':'None allocated','cu_estimate':0,'allocation_minutes':0}
verdict=ss[-1]['verdict'] if ss else 'STILL INCONCLUSIVE'
def ci(x,k=1):return f'[{x[0]*k:.2f}, {x[1]*k:.2f}]'
lines=['# 027r: DiffusionGemma fair GSM8K quality comparison','',f'**Verdict: {verdict}.**','', 'This is the fresh 2026-10-15 recovery requested after the earlier infrastructure failures. Hypothesis: DiffusionGemma Q4_K_M is more accurate than autoregressive Gemma 4 Q4_K_M on GSM8K with thinking disabled. Both models receive byte-identical rendered prompts, an empty thought channel, a 4096-token cap, context 8192 and eight CPU expert layers. DG uses its native entropy-bound sampler; AR is greedy. Conclusions concern these model/decoder combinations.','', '| Look | Paired n | DG correct, Wilson 95% CI | AR correct, Wilson 95% CI | DG−AR pp, paired bootstrap 95% CI | DG-only / AR-only | Exact McNemar p | Verdict |','|---|---:|---|---|---|---:|---:|---|']
for s in ss:
 a,b=s['dg'],s['ar'];lines.append(f"| {s['round']} | {s['n']}/{s['target']} | {a['correct']} ({ci(a['accuracy_ci'],100)}%) | {b['correct']} ({ci(b['accuracy_ci'],100)}%) | {s['difference']*100:+.2f} {ci(s['difference_ci'],100)} | {s['dg_only']} / {s['ar_only']} | {s['mcnemar_p']:.6g} | {s['verdict']} |")
if not ss:lines+=['| — | 0/150 | Unavailable | Unavailable | Not estimable | — | Not estimable | STILL INCONCLUSIVE |']
lines+=['','The rule was written before new inference: first test n=150 paired test questions sampled in retained seed-27 order. If inconclusive, expand once to cumulative n=300 with 150 new questions and reverse model execution order. At either of these two fixed looks, a two-sided exact McNemar p<.025 proves the direction of the measured difference (Bonferroni familywise alpha ≤.05). Stop after two looks. Nonsignificance does not demonstrate equivalence. Intervals use 20,000 paired bootstrap samples with seed 2702 and are descriptive 95% intervals; the exact test determines the verdict.','']
if ss:
 s=ss[-1];lines+=['| Model | Median useful tokens/s | Bootstrap 95% CI | Suspected cap hits | Missing explicit answer |','|---|---:|---|---:|---:|']
 for arm,label in [('dg','DiffusionGemma'),('ar','Gemma 4')]:
  a=s[arm];lines.append(f"| {label} | {a['median_tokens_s']:.2f} | {ci(a['median_speed_ci'])} | {a['cap_suspect']} | {a['missing_answer']} |")
 lines+=['',f"Paired-bootstrap 95% CI for DG minus AR median throughput: {ci(s['median_speed_difference_ci'])} tokens/s.",'']
 if s['verdict']=='STILL INCONCLUSIVE':lines+=['The fair comparison does not settle a directional quality advantage under the preregistered rule. No third scored round was run.','']
 if not s['complete']:lines+=['The last sample is incomplete. Its estimates are descriptive and cannot trigger the fixed-sample decision rule.','']
lines+=['Useful response tokens are counted with the same retained Gemma tokenizer, excluding diffusion canvas padding. Denominators include prompt processing and generation, exclude loading: DG engine turn time and AR prompt_ms + predicted_ms. This is turn throughput on these questions and this GPU, rather than a general decode-kernel claim. GPU offload is matched. Native sampler differences and running one arm before the other within each round remain limitations. DG cap hits are conservative (16 blocks); AR cap hits come from engine stop metadata.','', 'Scoring requires the final explicit `Answer: <number>` marker and exact decimal equality to the public GSM8K gold answer. Missing answers count as wrong. Both arms use the same parser. Nonempty emitted thought channels invalidate analysis. The DG adapter only disables automatic template rendering and adds an independent-input file loop; each response rebuilds the prefix. Its exact patch and source commit are retained. Raw outputs are copied to this workspace throughout execution, including incomplete work.','', f"Compute for this newly authorized attempt: GPU **{c['gpu']}**, allocation {c['allocation_minutes']:.2f} min, **{c['cu_estimate']:.3f} CU estimated** at 1.54 CU/hour. Exact experiment-only billed CU is unavailable on the shared account; before/after usage snapshots and allocation timestamps are retained. Prior failed attempts' ~5.290 CU lifetime estimate is historical and separate. This request authorized a new attempt capped at 5 CU. No A100 was used. See results/stop.txt for cleanup evidence.",'', 'The initial L4 request was refused while two other assignments were active. Retry evidence and account-balance checks are retained; other sessions were not stopped. An external 180-minute stop watchdog bounds this attempt to about 4.62 CU plus CLI overhead.','', 'Artifacts: results/raw/ contains responses, timing files, native logs and the C++ patch; results/per_response.json contains the scores; results/summary.json contains fixed-look inference. Reproduce analysis with `../.venv/bin/python scripts/analyze.py` and `../.venv/bin/python scripts/report.py` from this attempt folder. Original 027 files were not changed.','', 'Public sources: [GSM8K test questions](https://github.com/openai/grade-school-math/blob/master/grade_school_math/data/test.jsonl), [DiffusionGemma implementation](https://github.com/ggml-org/llama.cpp/pull/24423), [Gemma chat template](https://huggingface.co/unsloth/gemma-4-26B-A4B-it/blob/main/tokenizer_config.json).']
if (R/'failure.txt').exists():lines+=['','Execution limitation: '+(R/'failure.txt').read_text().splitlines()[-1]]
text='\n'.join(lines)+'\n';(ROOT/'writeup.md').write_text(text)
fig,axes=plt.subplots(1,2,figsize=(10,4))
if ss:
 s=ss[-1]
 for i,arm in enumerate(['dg','ar']):
  a=s[arm];v=a['accuracy']*100;lo,hi=a['accuracy_ci'];axes[0].bar(i,v,color=['#237aab','#e29435'][i]);axes[0].errorbar(i,v,yerr=[[v-lo*100],[hi*100-v]],fmt='none',capsize=4,color='black')
  v=a['median_tokens_s'];lo,hi=a['median_speed_ci'];axes[1].bar(i,v,color=['#237aab','#e29435'][i]);axes[1].errorbar(i,v,yerr=[[v-lo],[hi-v]],fmt='none',capsize=4,color='black')
 for ax in axes:ax.set_xticks([0,1],['DiffusionGemma','Gemma 4'])
 axes[0].set_ylim(0,105);axes[0].set_ylabel('Accuracy %, Wilson 95% CI');axes[1].set_ylabel('Useful tokens/s, bootstrap 95% CI');fig.suptitle(f"Fair GSM8K: n={s['n']}, {verdict}")
else:
 for ax in axes:ax.text(.5,.5,'No valid paired measurements\nCIs not estimable',ha='center',va='center');ax.set_axis_off()
 fig.suptitle('027r: STILL INCONCLUSIVE')
fig.tight_layout();fig.savefig(ROOT/'chart.png',dpi=180)
# Preserve prior committed failure records before replacing the landing documents.
for name in ['README.md','writeup.md','chart.png']:
 dst=ROOT/('historical_'+name)
 if not dst.exists():shutil.copy2(PARENT/name,dst)
shutil.copy2(ROOT/'writeup.md',PARENT/'writeup.md');shutil.copy2(ROOT/'chart.png',PARENT/'chart.png')
prereg=(ROOT/'README.md').read_text().split('\n## Latest result')[0]
result='\n## Latest result\n\n'+f'Verdict: **{verdict}**. GPU: {c["gpu"]}; this fresh attempt used approximately {c["cu_estimate"]:.3f} CU. '
if ss:
 s=ss[-1];result+=f"DG {s['dg']['correct']}/{s['n']} vs AR {s['ar']['correct']}/{s['n']}; McNemar p={s['mcnemar_p']:.6g}; difference {s['difference']*100:+.2f} pp, 95% CI {ci(s['difference_ci'],100)}. "
result+='See [writeup.md](writeup.md) and chart.png. Earlier failure records are retained as historical_* in this attempt folder.\n'
(ROOT/'README.md').write_text(prereg+result)
(PARENT/'README.md').write_text(prereg+result+'\nThe authoritative fresh artifacts are in `attempt_20261015b/`. Historical failed run artifacts remain under `results/` and prior scripts; see `attempt_20261015b/historical_README.md`.\n')
print(verdict)
