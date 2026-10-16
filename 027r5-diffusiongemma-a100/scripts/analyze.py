import json,re,math,pathlib,hashlib
from decimal import Decimal,InvalidOperation
import numpy as np
from scipy.stats import binomtest,t,norm
from tokenizers import Tokenizer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results';D=R/'raw/answers'
P=json.load(open(ROOT/'scripts/prompts.json'));T=Tokenizer.from_file(str(R/'tokenizer.json'))
def wilson(k,n):
 z=norm.ppf(.975);p=k/n;den=1+z*z/n;c=(p+z*z/(2*n))/den;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return [c-h,c+h]
def parse(arm,i):
 f=D/f'{arm}_{i}.json'
 if not f.exists():return None
 d=json.load(open(f));assert d['id']==P[i]['id']
 reply=d['text'] if arm=='dg' else d['content']
 ms=d['milliseconds'] if arm=='dg' else d['timings']['prompt_ms']+d['timings']['predicted_ms']
 m=re.findall(r'Answer:\s*\$?\s*([-+]?\d[\d,]*(?:\.\d+)?)',reply,re.I)
 fallback=not bool(m)
 if fallback:m=re.findall(r'[-+]?\d[\d,]*(?:\.\d+)?',reply)
 pred=m[-1].replace(',','') if m else None
 try:correct=Decimal(pred)==Decimal(P[i]['gold'].replace(',',''))
 except (TypeError,InvalidOperation):correct=False
 tokens=len(T.encode(reply,add_special_tokens=False).ids)
 return dict(arm=arm,index=i,id=P[i]['id'],prediction=pred,gold=P[i]['gold'],correct=bool(correct),fallback=fallback,useful_tokens=tokens,time_ms=ms,tokens_s=tokens*1000/ms,reply=reply,prompt_sha256=hashlib.sha256(P[i]['rendered'].encode()).hexdigest(),cap_reached=(d.get('tokens_predicted',0)>=384 if arm=='ar' else tokens>=384),nonempty_thought=any(s.strip() for s in re.findall(r'<\|channel>thought(.*?)(?:<channel\|>|$)',reply,re.S)))
def analyze():
 rows=[];pairs=[]
 for i in range(200):
  a,b=parse('dg',i),parse('ar',i)
  rows.extend(x for x in [a,b] if x)
  if a and b:pairs.append((a,b))
 n=len(pairs);s=dict(n=n,target=200,complete=n==200,verdict='STILL INCONCLUSIVE',available={a:sum(x['arm']==a for x in rows) for a in ['dg','ar']})
 if n:
  delta=np.array([int(a['correct'])-int(b['correct']) for a,b in pairs]);mean=float(delta.mean());se=float(delta.std(ddof=1)/np.sqrt(n)) if n>1 else float('nan');w=int(sum(delta==1));l=int(sum(delta==-1));pv=float(binomtest(w,w+l).pvalue) if w+l else 1.
  ci95=[mean-t.ppf(.975,n-1)*se,mean+t.ppf(.975,n-1)*se];ci90=[mean-t.ppf(.95,n-1)*se,mean+t.ppf(.95,n-1)*se]
  if se>0:pl=float(t.sf((mean+.06)/se,n-1));pu=float(t.cdf((mean-.06)/se,n-1))
  else:pl=0. if mean>-.06 else 1.;pu=0. if mean<.06 else 1.
  s.update(difference=mean,difference_ci95=ci95,difference_ci90=ci90,dg_only=w,ar_only=l,mcnemar_p=pv,tost_lower_p=pl,tost_upper_p=pu,equivalent=pl<.05 and pu<.05)
  rng=np.random.default_rng(2703);ix=rng.integers(n,size=(20000,n))
  for arm,j in [('dg',0),('ar',1)]:
   aa=[p[j] for p in pairs];k=sum(r['correct'] for r in aa);sp=np.array([r['tokens_s'] for r in aa]);s[arm]=dict(correct=k,accuracy=k/n,accuracy_ci95=wilson(k,n),median_tokens_s=float(np.median(sp)),median_speed_ci95=np.quantile(np.median(sp[ix],axis=1),[.025,.975]).tolist(),fallback=sum(r['fallback'] for r in aa),cap_reached=sum(r['cap_reached'] for r in aa),nonempty_thought=sum(r['nonempty_thought'] for r in aa))
  if n==200:
   if pv<.05:s.update(verdict='PROVEN' if mean>0 else 'DISPROVEN',reason='superiority' if mean>0 else 'inferiority')
   elif s['equivalent']:s.update(verdict='DISPROVEN',reason='equivalent within ±6 percentage points')
   else:s.update(reason='Neither test resolved the fixed sample; no further sampling authorized within the budget.')
 (R/'per_response.json').write_text(json.dumps(rows,indent=2));(R/'summary.json').write_text(json.dumps(s,indent=2))
 power=[]
 for q in [.05,.1,.15,.2]:
  se=np.sqrt(q/200);eq=max(0,2*norm.cdf(.06/se-norm.ppf(.95))-1);sd=np.sqrt((q-.08**2)/200);sup=norm.sf(norm.ppf(.975)-.08/sd)+norm.cdf(-norm.ppf(.975)-.08/sd)
  power.append(dict(discordance=q,equivalence_power=float(eq),superiority_power_at_8pp=float(sup) if q>=.08 else None))
 (R/'power.json').write_text(json.dumps(power,indent=2))
 return s
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
