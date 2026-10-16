import json,re,math,pathlib,sys
from decimal import Decimal,InvalidOperation
import numpy as np
from scipy.stats import binomtest
from tokenizers import Tokenizer
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results';RAW=R/'raw'
P=json.load(open(ROOT.parent/'scripts/prompts.json'))[:300]
T=Tokenizer.from_file(str(ROOT.parent/'results/tokenizer.json'))
def wilson(k,n):
 z=1.95996398454;p=k/n;den=1+z*z/n;c=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return [c-h,c+h]
def parse(p,arm,i,rd):
 D=RAW/f'round{rd}'
 if arm=='dg':
  if not (D/f'dg_{i}.done').exists():return None
  reply=(D/f'dg_{i}.out').read_text();ms=float((D/f'dg_{i}.ms').read_text());steps,blocks=map(int,(D/f'dg_{i}.done').read_text().split());cap=blocks>=16
  if not steps or not blocks:raise ValueError('DG generation failed')
 else:
  f=D/f'ar_{i}.json'
  if not f.exists():return None
  d=json.load(f.open());reply=d['content'];ms=d['timings']['prompt_ms']+d['timings']['predicted_ms'];cap=d.get('stopped_limit',False) or d.get('stop_type')=='limit' or d.get('tokens_predicted',0)>=4096
 if any(t.strip() for t in re.findall(r'<\|channel>thought(.*?)(?:<channel\|>|$)',reply,re.S)):raise ValueError('nonempty thought channel')
 # Explicit final Answer marker is required, as preregistered; no numerical fallback.
 m=re.findall(r'Answer:\s*\$?\s*([-+]?\d[\d,]*(?:\.\d+)?)',reply,re.I)
 pred=m[-1].replace(',','') if m else None
 try:correct=Decimal(pred)==Decimal(p['gold'].replace(',',''))
 except (TypeError,InvalidOperation):correct=False
 n=len(T.encode(reply,add_special_tokens=False).ids)
 return dict(id=p['id'],round=rd,arm=arm,gold=p['gold'],prediction=pred,correct=correct,reply=reply,useful_tokens=n,time_ms=ms,tokens_s=n*1000/ms,cap_suspect=bool(cap),prompt_sha256=__import__('hashlib').sha256(p['rendered'].encode()).hexdigest())
def analyze():
 rows=[];pairs=[];summ=[]
 for rd,target in [(1,150),(2,300)]:
  new=[]
  for i,p in enumerate(P[(rd-1)*150:rd*150]):
   a=parse(p,'dg',i,rd);b=parse(p,'ar',i,rd)
   rows.extend(x for x in [a,b] if x)
   if a and b:new.append((a,b))
  if not new:continue
  pairs+=new;n=len(pairs);delta=np.array([int(a['correct'])-int(b['correct']) for a,b in pairs]);w=int(sum(delta==1));l=int(sum(delta==-1));pv=float(binomtest(w,w+l).pvalue) if w+l else 1.
  rng=np.random.default_rng(2702);ix=rng.integers(n,size=(20000,n));ci=np.quantile(delta[ix].mean(axis=1),[.025,.975]).tolist()
  s=dict(round=rd,n=n,target=target,complete=n==target,dg_only=w,ar_only=l,mcnemar_p=pv,difference=float(delta.mean()),difference_ci=ci,verdict=('PROVEN' if w>l else 'DISPROVEN') if n==target and pv<.025 else 'STILL INCONCLUSIVE')
  for arm,j in [('dg',0),('ar',1)]:
   aa=[p[j] for p in pairs];k=sum(r['correct'] for r in aa);speeds=np.array([r['tokens_s'] for r in aa]);s[arm]=dict(correct=k,accuracy=k/n,accuracy_ci=wilson(k,n),median_tokens_s=float(np.median(speeds)),median_speed_ci=np.quantile(np.median(speeds[ix],axis=1),[.025,.975]).tolist(),missing_answer=sum(r['prediction'] is None for r in aa),cap_suspect=sum(r['cap_suspect'] for r in aa))
  sp=np.array([[a['tokens_s'],b['tokens_s']] for a,b in pairs]);s['median_speed_difference_ci']=np.quantile(np.median(sp[ix,0],axis=1)-np.median(sp[ix,1],axis=1),[.025,.975]).tolist();summ.append(s)
 (R/'per_response.json').write_text(json.dumps(rows,indent=2));(R/'summary.json').write_text(json.dumps(summ,indent=2))
 return summ
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
