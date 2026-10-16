"""Produce an honest report from retained allocation/progress evidence only."""
import json, pathlib, datetime
R=pathlib.Path(__file__).resolve().parents[1]; O=R/'results'
events=[]; allocations=[]
for filename in ['initial_history.jsonl','recovery_history.jsonl']:
 ds=[json.loads(line) for line in (O/filename).read_text().splitlines()]
 start=next(d for d in ds if d['event_type']=='session_created');end=next(d for d in reversed(ds) if d['event_type']=='session_terminated')
 minutes=(datetime.datetime.fromisoformat(end['timestamp'])-datetime.datetime.fromisoformat(start['timestamp'])).total_seconds()/60
 allocations.append({'history':filename,'start':start['timestamp'],'pruned':end['timestamp'],'gpu':'L4','minutes_upper':minutes,'cu_upper_at_1_54_per_hour':minutes*1.54/60})
 for d in ds:
  if d['event_type'] in ['session_created','session_terminated']:
   events.append({k:v for k,v in d.items() if k!='endpoint'})
  if d['event_type']=='execution':
   for out in d.get('outputs',[]):
    text=out.get('text','')
    if 'round 1 dg 144/150' in text or 'Scored round 1 launched: 150 pairs' in text:
     events.append({'timestamp':d['timestamp'],'event_type':'retained_progress','text':text})
cu=sum(a['cu_upper_at_1_54_per_hour'] for a in allocations)
json.dump(events,open(O/'retained_evidence.json','w'),indent=2)
json.dump({'allocations':allocations,'total_cu_upper_estimate':cu,'rate_cu_hour':1.54,'exact_billed_cu':None,'notes':'Pruning timestamps bound allocation lifetime, not exact billed GPU time. Shared account balance cannot isolate this experiment. No further allocation.'},open(O/'final_compute.json','w'),indent=2)
s={'verdict':'STILL INCONCLUSIVE','validated_pairs':0,'last_observed_dg_count':144,'last_observed_ar_count':0,'target_round_1':150,'round_2_launched':False,'accuracy':None,'accuracy_ci':None,'mcnemar_p':None,'tokens_s':None,'speed_ci':None,'missing_scored_artifacts':True}
json.dump(s,open(O/'summary.json','w'),indent=2)
report=f'''# 027r: fair DiffusionGemma quality comparison

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

Recovery found no active Colab assignments. Explicit stop calls for this experiment's two names returned “not found”; no other session was touched. Initial setup and recovery each used L4 (no A100). The session histories show allocation windows {allocations[0]['minutes_upper']:.2f} and {allocations[1]['minutes_upper']:.2f} minutes. At the recorded 1.54 CU/hour rate, their combined lifetime-based upper estimate is **{cu:.3f} CU**. Exact billed experiment-only CU is unavailable: this is a shared account, and pruning time may follow actual GPU termination. The conservative estimate slightly exceeds the 5-CU cap, so budget compliance cannot be certified. No further GPU run was started. The local watchdog's stop was not recorded; the earlier README's intended deadline must not be mistaken for confirmed termination.

This is one interrupted scored round, not two completed rounds. A second redesign/rerun was not possible within the remaining defensible budget. The requested inferential experiment remains unfinished; claiming PROVEN or DISPROVEN would fabricate evidence. A future authorized attempt should download each completed response immediately, enforce cleanup outside the notebook, and budget from actual session lifetimes. It would require a fresh compute allowance.

Artifacts: `results/retained_evidence.json` contains only public experiment progress and allocation timestamps; `results/final_compute.json` records accounting; `results/summary.json` uses null for missing measurements. Existing scripts and public GSM8K questions are retained for reproducibility. Raw CLI history exports are excluded from the commit because they contain environment-specific execution payloads.
'''
(R/'writeup.md').write_text(report)
readme=R/'README.md'
readme.write_text(readme.read_text().split('\n## Final recovery outcome\n')[0]+'\n## Final recovery outcome\n\n'+report.split('\n\n',1)[1]+'\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,4.5));ax.axis('off')
ax.text(.5,.87,'027r — STILL INCONCLUSIVE',ha='center',fontsize=20,weight='bold')
ax.text(.5,.65,'No recovered scored pairs',ha='center',fontsize=17)
ax.text(.5,.45,'Last saved progress: DG 144/150 · Gemma 4 0/150\nTarget: 150 paired questions; round 2 never launched',ha='center',fontsize=12)
ax.text(.5,.2,'Accuracy, confidence intervals and same-run tokens/s: unavailable\nProgress counts are not quality measurements.',ha='center',fontsize=11)
fig.savefig(R/'chart.png',dpi=180,bbox_inches='tight');plt.close(fig)
print(json.dumps({'verdict':s['verdict'],'cu_upper':cu},indent=2))
