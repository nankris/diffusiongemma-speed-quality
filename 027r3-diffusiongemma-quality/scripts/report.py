import pathlib,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results'
s=json.load(open(R/'summary.json'));c=json.load(open(R/'compute.json'))
def pct(x):return f'{100*x:.2f}%'
def ci(x,percent=False):return '['+', '.join(pct(y) if percent else f'{y:.2f}' for y in x)+']'
lines=['# Round 3: DiffusionGemma versus Gemma 4 quality','',f"**Verdict: {s['verdict']}** — {s.get('reason','Budget exhausted before the fixed paired sample was complete.')}",'',f"Recovered {s['available']['dg']} DG and {s['available']['ar']} AR responses; {s['n']}/300 paired questions.",'','| Measure | DiffusionGemma | Gemma 4 AR |','|---|---:|---:|']
if s['n']:
 lines.extend([f"| Correct / paired items | {s['dg']['correct']}/{s['n']} | {s['ar']['correct']}/{s['n']} |",f"| Accuracy (Wilson 95% CI) | {pct(s['dg']['accuracy'])} {ci(s['dg']['accuracy_ci95'],True)} | {pct(s['ar']['accuracy'])} {ci(s['ar']['accuracy_ci95'],True)} |",f"| Median useful tokens/s (bootstrap 95% CI) | {s['dg']['median_tokens_s']:.2f} {ci(s['dg']['median_speed_ci95'])} | {s['ar']['median_tokens_s']:.2f} {ci(s['ar']['median_speed_ci95'])} |",'',f"DG minus AR: **{100*s['difference']:.2f} percentage points**, paired t 95% CI {ci(s['difference_ci95'],True)}; 90% CI {ci(s['difference_ci90'],True)}. DG-only successes {s['dg_only']}; AR-only successes {s['ar_only']}. Exact two-sided McNemar p={s['mcnemar_p']:.6g}. TOST lower p={s['tost_lower_p']:.6g}, upper p={s['tost_upper_p']:.6g}; margin ±5 percentage points.",'',f"Numerical fallback used: DG {s['dg']['fallback']}, AR {s['ar']['fallback']}. Nonempty generated thought channels: DG {s['dg']['nonempty_thought']}, AR {s['ar']['nonempty_thought']}."])
else:lines+=['| Accuracy | Unavailable | Unavailable |','| Useful tokens/s | Unavailable | Unavailable |','','No paired CI or test is estimable.']
lines+=['',f"Compute: {c['gpu']}, {c['allocation_minutes']:.2f} allocation minutes × {c['rate_cu_per_hour']:.2f} CU/hour = **{c['cu_estimate']:.3f} CU** allocation-lifetime estimate (not exact billing). Explicit stop recorded in results/stop.txt. Initial shared account balance 174.92 CU. Other sessions were not stopped.",'','Inference is limited to this public GSM8K sample, these Q4_K_M artifacts, native DG sampler versus greedy AR, thinking disabled, 4096-token cap, eight CPU expert layers, and one L4. Throughput counts useful shared-tokenizer output tokens per prompt-plus-generation time, excluding loading; do not compare directly with earlier fully GPU-offloaded speed results. A single fixed inferential look was planned; no interim accuracy tests were used. Equivalence does not mean identical answers or equal performance on other tasks. Public benchmark training contamination cannot be excluded.','', 'Reproduce: create a venv, install requirements.txt, obtain the public tokenizer using scripts/get_tokenizer.py, then run scripts/analyze.py and scripts/report.py. Raw per-item replies and engine timings are under results/raw/answers; prompt text, IDs, gold values and rendered input are in scripts/prompts.json. See scripts/controller.py for allocation monitoring and synchronous batch recovery.','', 'Model sources: [DG Q4_K_M](https://huggingface.co/unsloth/diffusiongemma-26B-A4B-it-GGUF), [AR Q4_K_M](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF); [GSM8K test](https://github.com/openai/grade-school-math/blob/master/grade_school_math/data/test.jsonl).']
(ROOT/'writeup.md').write_text('\n'.join(lines)+'\n')
fig,ax=plt.subplots(1,3,figsize=(13,4),layout='constrained')
if s['n']:
 for j,arm in enumerate(['dg','ar']):
  a=s[arm];v=100*a['accuracy'];lo,hi=np.array(a['accuracy_ci95'])*100;ax[0].errorbar(j,v,yerr=[[v-lo],[hi-v]],fmt='o',capsize=5,color=['#2878b5','#dc8b24'][j])
  v=a['median_tokens_s'];lo,hi=a['median_speed_ci95'];ax[2].errorbar(j,v,yerr=[[v-lo],[hi-v]],fmt='o',capsize=5,color=['#2878b5','#dc8b24'][j])
 v=s['difference']*100;lo,hi=np.array(s['difference_ci95'])*100;ax[1].axvspan(-5,5,alpha=.15,color='green');ax[1].axvline(0,color='grey',lw=1);ax[1].errorbar(v,0,xerr=[[v-lo],[hi-v]],fmt='o',capsize=5,color='#2878b5');ax[1].set_yticks([]);ax[1].set_xlabel('DG − AR (percentage points)');ax[1].set_title('Paired difference, 95% CI\nShading: ±5-point equivalence margin')
else:
 for a in ax:a.text(.5,.5,'No paired measurements',ha='center',transform=a.transAxes)
for j in [0,2]:ax[j].set_xticks([0,1],['DiffusionGemma','Gemma 4 AR']);ax[j].set_xlim(-.5,1.5)
ax[0].set_ylabel('Accuracy (%)');ax[0].set_title('Accuracy, Wilson 95% CI');ax[2].set_ylabel('Useful output tokens/s');ax[2].set_title('Median throughput, bootstrap 95% CI')
fig.suptitle(f"{s['verdict']} | n={s['n']} paired GSM8K questions | one L4")
fig.savefig(ROOT/'chart.png',dpi=180);plt.close(fig)
