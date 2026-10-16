"""Paired analysis; reads results/rows.jsonl, preserving missing pairs as missing."""
import json,re
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def wilson(k,n):
 z=1.95996398454;p=k/n;d=1+z*z/n
 m=(p+z*z/(2*n))/d;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [m-h,m+h]
def summarize(rows,n):
 by={}
 for r in rows:by.setdefault(r['id'],{})[r['arm']]=r
 pairs=[v for v in by.values() if all(a in v and v[a].get('valid',False) for a in ['dg','ar'])][:n]
 if not pairs:return dict(n=0,verdict='STILL INCONCLUSIVE')
 d=np.array([p['dg']['correct']-p['ar']['correct'] for p in pairs],dtype=int)
 b=int((d==1).sum());c=int((d==-1).sum());p=binomtest(b,b+c).pvalue if b+c else 1.
 rng=np.random.default_rng(2701)
 boot=np.array([rng.choice(d,len(d),replace=True).mean() for _ in range(20000)])
 s=dict(n=len(d),dg_only=b,ar_only=c,mcnemar_p=p,difference=float(d.mean()),difference_ci95=np.quantile(boot,[.025,.975]).tolist())
 for a in ['dg','ar']:
  rr=[v[a] for v in pairs];k=sum(r['correct'] for r in rr)
  speed=[r['tokens_s'] for r in rr if r.get('tokens_s') is not None]
  s[a]=dict(correct=k,accuracy=k/len(d),ci95=wilson(k,len(d)),cap_hits=sum(r.get('cap_hit',False) for r in rr),median_tokens_s=float(np.median(speed)) if speed else None)
 fair=s['dg']['cap_hits']==s['ar']['cap_hits']==0
 s['verdict']=('PROVEN' if b>c else 'DISPROVEN') if p<.025 and fair and len(d)>=n else 'STILL INCONCLUSIVE'
 return s
if __name__=='__main__':
 rows=[json.loads(l) for l in (ROOT/'results/rows.jsonl').read_text().splitlines()]
 out=[summarize(rows,150)]
 if out[0]['verdict']=='STILL INCONCLUSIVE':out.append(summarize(rows,500))
 (ROOT/'results/summary.json').write_text(json.dumps(out,indent=2))
 print(json.dumps(out,indent=2))
 s=out[-1];fig,ax=plt.subplots(1,2,figsize=(9,4))
 if s['n']:
  for i,a in enumerate(['dg','ar']):
   v=s[a];lo,hi=v['ci95'];ax[0].bar(i,v['accuracy']*100,color=['#239b75','#808898'][i]);ax[0].errorbar(i,v['accuracy']*100,yerr=[[100*(v['accuracy']-lo)],[100*(hi-v['accuracy'])]],color='black',capsize=4)
   ax[1].bar(i,v['median_tokens_s'] or 0,color=['#239b75','#808898'][i])
  for a in ax:a.set_xticks([0,1],['DiffusionGemma','Gemma 4'])
  ax[0].set_ylabel('Accuracy %, Wilson 95% CI');ax[0].set_ylim(0,100);ax[1].set_ylabel('Median useful output tokens/s')
 fig.suptitle(f"027r: n={s['n']} paired GSM8K questions — {s['verdict']}")
 fig.tight_layout();fig.savefig(ROOT/'chart.png',dpi=180)
