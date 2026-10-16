import pathlib,json,re,math,statistics,csv
import numpy as np
from tokenizers import Tokenizer
from scipy.stats import binomtest
R=pathlib.Path(__file__).resolve().parents[1]/'results'
tok=Tokenizer.from_file(str(R/'tokenizer.json'))
items=json.load(open(R/'items.json'))
def wilson(k,n):
 z=1.95996398454;p=k/n;den=1+z*z/n
 c=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return [c-h,c+h]
def extract(text,arm):
 if arm=='dg': return text.split('\ntotal time:')[0].strip()
 return text.split('\nmodel\n',1)[-1].replace('[end of text]','').strip()
def rows():
 result=[]
 for ix,item in enumerate(items):
  pair={'index':ix,'id':item['id'],'gold':item['gold']}
  for arm in ['dg','ar']:
   stem=R/'raw'/f'{ix:03}_{arm}'
   if not stem.with_suffix('.json').exists():break
   meta=json.load(open(stem.with_suffix('.json')))
   if meta['returncode']:break
   out=stem.with_suffix('.out').read_text();err=stem.with_suffix('.err').read_text();reply=extract(out,arm)
   thoughts=re.findall(r'<\|channel>thought(.*?)(?:<channel\|>|$)',reply,re.S)
   if any(t.strip() for t in thoughts):raise ValueError(f'Thinking enabled {ix} {arm}')
   matches=re.findall(r'####\s*\$?\s*([-+]?\d[\d,]*(?:\.\d+)?)',reply)
   pred=matches[-1].replace(',','') if matches else None
   correct=pred is not None and float(pred)==float(item['gold'].replace(',',''))
   nt=len(tok.encode(reply,add_special_tokens=False).ids)
   if arm=='dg':
    m=re.search(r'total time: ([\d.]+)ms',out);secs=float(m[1])/1000 if m else None
   else:
    m=re.search(r'(?<!prompt )eval time =\s+([\d.]+) ms /\s+(\d+) runs',err);secs=float(m[1])/1000 if m else None
    pe=re.search(r'prompt eval time =\s+([\d.]+) ms',err)
    if secs is not None and pe: secs+=float(pe[1])/1000
   api=stem.with_suffix('.api.json')
   capped=nt>=4090
   if api.exists():
    data=json.load(open(api));times=data['timings'];secs=(times['prompt_ms']+times['predicted_ms'])/1000
    capped=bool(data.get('truncated')) or bool(data.get('stopped_limit'))
   pair.update({arm+'_correct':correct,arm+'_pred':pred,arm+'_tokens':nt,arm+'_useful_tps':nt/secs if secs else None,arm+'_decode_s':secs,arm+'_wall_s':meta['wall_s'],arm+'_cap_hit':capped})
  else:
   result.append(pair);continue
  break
 return result
def summary(rr):
 n=len(rr);d=np.array([int(r['dg_correct'])-int(r['ar_correct']) for r in rr]);b=sum(d==1);c=sum(d==-1)
 p=binomtest(int(b),int(b+c),.5).pvalue if b+c else 1.
 rng=np.random.default_rng(2702);boots=np.array([rng.choice(d,(1000,n)).mean(axis=1) for _ in range(20)]).ravel()
 s={'n':n,'dg_only':int(b),'ar_only':int(c),'mcnemar_p':p,'difference':float(d.mean()),'difference_ci_97_5':np.quantile(boots,[.0125,.9875]).tolist(),'verdict':('PROVEN' if b>c else 'DISPROVEN') if p<.025 else 'STILL INCONCLUSIVE'}
 for arm in ['dg','ar']:
  k=sum(r[arm+'_correct'] for r in rr)
  rates=[r[arm+'_useful_tps'] for r in rr if r[arm+'_useful_tps'] is not None]
  rb=np.array([np.median(rng.choice(rates,(1000,len(rates))),axis=1) for _ in range(10)]).ravel() if rates else []
  s[arm]={'correct':k,'accuracy':k/n,'accuracy_ci_95':wilson(k,n),'median_useful_tps':statistics.median(rates) if rates else None,'median_tps_ci_95':np.quantile(rb,[.025,.975]).tolist() if rates else None,'total_wall_s':sum(r[arm+'_wall_s'] for r in rr),'cap_hits':sum(r[arm+'_cap_hit'] for r in rr)}
 return s
if __name__=='__main__':
 rr=rows();json.dump(rr,open(R/'per_item.json','w'),indent=2)
 if not rr:raise SystemExit('No complete validated pairs')
 with open(R/'per_item.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 ss={str(n):summary(rr[:n]) for n in [150,400] if len(rr)>=n}
 if not ss:ss={'partial':summary(rr)}
 json.dump(ss,open(R/'summary.json','w'),indent=2);print(json.dumps(ss,indent=2))
