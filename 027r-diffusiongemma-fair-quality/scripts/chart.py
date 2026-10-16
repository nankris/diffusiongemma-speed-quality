import pathlib,json,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=pathlib.Path(__file__).resolve().parents[1];ss=json.load(open(P/'results/summary.json'));s=list(ss.values())[-1]
fig,(a,b)=plt.subplots(1,2,figsize=(10,4.2))
colors=['#208b68','#687487'];labels=['DiffusionGemma','Gemma 4']
for i,arm in enumerate(['dg','ar']):
 v=s[arm];lo,hi=v['accuracy_ci_95'];acc=v['accuracy']
 a.bar(i,100*acc,color=colors[i]);a.errorbar(i,acc*100,yerr=[[100*(acc-lo)],[100*(hi-acc)]],fmt='none',color='black',capsize=5)
 a.text(i,acc*100+5,f"{v['correct']}/{s['n']}",ha='center')
 t=v['median_useful_tps'];lo,hi=v['median_tps_ci_95']
 b.bar(i,t,color=colors[i]);b.errorbar(i,t,yerr=[[t-lo],[hi-t]],fmt='none',color='black',capsize=5);b.text(i,hi+1,f'{t:.1f}',ha='center')
a.set_ylim(0,110);a.set_ylabel('Exact-answer accuracy (%)');a.set_title('GSM8K: thinking off, matched prompts\n95% Wilson intervals')
b.set_ylabel('Useful output tokens / second');b.set_title('L4: prefill + generation, loading excluded\nMedian with 95% bootstrap intervals')
for ax in (a,b):ax.set_xticks([0,1],labels);ax.spines[['top','right']].set_visible(False)
lo,hi=s['difference_ci_97_5'];fig.suptitle(f"{s['verdict']} | n={s['n']} | DG minus Gemma 4: {100*s['difference']:+.1f} pp [{100*lo:+.1f}, {100*hi:+.1f}]\nExact McNemar p={s['mcnemar_p']:.4g}; 97.5% paired difference CI",fontsize=10)
fig.tight_layout();fig.savefig(P/'chart.png',dpi=160)
