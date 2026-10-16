import json,re,pathlib,sys
import numpy as np
from scipy.stats import binomtest
from tokenizers import Tokenizer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1]; R=ROOT/'results'; T=Tokenizer.from_file(str(R/'tokenizer.json'))
P=json.load(open(ROOT/'scripts/prompts.json')); rng=np.random.default_rng(27)
def wilson(k,n):
 z=1.95996398454;a=(k/n+z*z/(2*n))/(1+z*z/n);h=z*np.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n);return [a-h,a+h]
def boot(x,fn=np.mean):
 x=np.array(x);return np.quantile(fn(x[rng.integers(len(x),size=(20000,len(x)))],axis=1),[.025,.975]).tolist()
def parse(p,arm):
 stem=R/f"r{p['round']}_{arm}_{p['id']}";m=stem.with_suffix('.meta.json')
 if not m.exists():return None
 meta=json.load(open(m)); out=stem.with_suffix('.out').read_text();err=stem.with_suffix('.err').read_text()
 if meta['exit_code']:return None
 if arm=='dg':
  match=re.search(r'total time: ([\d.]+)ms',out+'\n'+err)
  body=re.split(r'\ntotal time:',out)[0].strip()
 else:
  match=re.search(r'eval time =\s+([\d.]+) ms /\s+(\d+) runs',err)
  # Skip the prompt-eval match.
  matches=re.findall(r'(?<!prompt )eval time =\s+([\d.]+) ms /\s+(\d+) runs',err)
  match=None if not matches else matches[-1]
  body=out.replace('[end of text]','').strip()
 n=len(T.encode(body,add_special_tokens=False).ids)
 api=stem.with_suffix('.api.json')
 if not match and not api.exists():return None
 if arm=='ar' and api.exists():
  data=json.load(open(api));ms=float(data['timings']['prompt_ms'])+float(data['timings']['predicted_ms'])
 else:ms=float(match.group(1)) if arm=='dg' else float(re.findall(r'total time =\s+([\d.]+) ms',err)[-1])
 ans=re.findall(r'Answer:\s*\$?\s*(-?[\d,]+(?:\.\d+)?)',body)
 val=ans[-1].replace(',','') if ans else None
 try:correct=float(val)==float(p['gold'].replace(',',''))
 except (TypeError,ValueError):correct=False
 return {**meta,'reply':body,'answer':val,'gold':p['gold'],'correct':correct,'useful_tokens':n,'time_ms':ms,'tokens_s':n/(ms/1000),'thought_channel_emitted':any(t.strip() for t in re.findall(r'<\|channel>thought(.*?)(?:<channel\|>|$)',body,re.S)),'cap_suspect':(bool(data.get('stopped_limit')) or bool(data.get('truncated')) or data.get('stop_type')=='limit' or data.get('tokens_predicted',0)>=4096) if arm=='ar' and api.exists() else n>=4090}
rows=[];summ=[]
for rd,target in [(1,150),(2,300)]:
 pairs=[]
 for p in P:
  if p['round']>rd or (p['round']==2 and P.index(p)>=300):continue
  a=parse(p,'dg');b=parse(p,'ar')
  for x in [a,b]:
   if x and not any(r['id']==x['id'] and r['arm']==x['arm'] for r in rows):rows.append(x)
  if a and b:
   if a['thought_channel_emitted'] or b['thought_channel_emitted']:raise ValueError('Thinking enabled; round invalid')
   if a.get('prompt')!=p['rendered'] or b.get('prompt')!=p['rendered']:raise ValueError('Prompt mismatch')
   pairs.append((a,b))
 if not pairs or (rd==2 and not any(x['round']==2 for pair in pairs for x in pair)):continue
 n=len(pairs);d=np.array([int(a['correct'])-int(b['correct']) for a,b in pairs]);w=int(sum(d==1));l=int(sum(d==-1));pv=binomtest(w,w+l).pvalue if w+l else 1.
 s={'round':rd,'n':n,'target':target,'complete':n==target,'dg_only':w,'ar_only':l,'mcnemar_p':pv,'difference':float(d.mean()),'difference_ci':boot(d),'verdict':'PROVEN' if n==target and pv<.025 and w>l else 'DISPROVEN' if n==target and pv<.025 and l>w else 'STILL INCONCLUSIVE'}
 for arm,i in [('dg',0),('ar',1)]:
  aa=[p[i] for p in pairs];k=sum(r['correct'] for r in aa);sp=[r['tokens_s'] for r in aa]
  s[arm]={'correct':k,'accuracy':k/n,'accuracy_ci':wilson(k,n),'median_tokens_s':float(np.median(sp)),'median_speed_ci':boot(sp,np.median),'missing_answer':sum(r['answer'] is None for r in aa),'cap_suspect':sum(r['cap_suspect'] for r in aa),'thought_channel_emitted':sum(r['thought_channel_emitted'] for r in aa)}
 sp=np.array([[a['tokens_s'],b['tokens_s']] for a,b in pairs]);ix=rng.integers(n,size=(20000,n));dif=np.median(sp[ix,0],axis=1)-np.median(sp[ix,1],axis=1);s['median_speed_difference_ci']=np.quantile(dif,[.025,.975]).tolist()
 summ.append(s)
json.dump(rows,open(R/'per_response.json','w'),indent=2);json.dump(summ,open(R/'summary.json','w'),indent=2);print(json.dumps(summ,indent=2))
fig,axes=plt.subplots(1,2,figsize=(10,4))
if summ:
 s=summ[-1]
 for i,arm in enumerate(['dg','ar']):
  a=s[arm];lo,hi=a['accuracy_ci'];axes[0].bar(i,a['accuracy']*100,color=['#22aa77','#888888'][i]);axes[0].errorbar(i,a['accuracy']*100,yerr=[[100*(a['accuracy']-lo)],[100*(hi-a['accuracy'])]],fmt='none',color='black',capsize=4)
  lo,hi=a['median_speed_ci'];axes[1].bar(i,a['median_tokens_s'],color=['#22aa77','#888888'][i]);axes[1].errorbar(i,a['median_tokens_s'],yerr=[[a['median_tokens_s']-lo],[hi-a['median_tokens_s']]],fmt='none',color='black',capsize=4)
 for a in axes:a.set_xticks([0,1],['DiffusionGemma','Gemma 4'])
 axes[0].set_ylabel('Accuracy %, Wilson 95% CI');axes[0].set_ylim(0,105);axes[1].set_ylabel('Useful tokens/s, bootstrap 95% CI');fig.suptitle(f"Round {s['round']}, paired n={s['n']}: {s['verdict']}")
else:
 for a in axes:a.text(.5,.5,'No valid paired observations',ha='center');a.set_axis_off()
fig.tight_layout();fig.savefig(ROOT/'chart.png',dpi=160)
