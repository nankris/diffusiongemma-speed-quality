"""Record the additional allocation, without manufacturing missing measurements."""
import json
from datetime import datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'results/final_compute.json'; d=json.loads(p.read_text())
start='2026-10-15T03:22:22.222141+00:00';stop='2026-10-15T03:32:41.277380+00:00'
seconds=(datetime.fromisoformat(stop)-datetime.fromisoformat(start)).total_seconds()
allocation=dict(start=start,stopped=stop,gpu='L4',minutes_upper=seconds/60,cu_upper_at_1_54_per_hour=seconds/3600*1.54,reason='Stopped during setup after discovering exhausted prior budget; no inference')
if not any(a.get('start')==start for a in d['allocations']):d['allocations'].append(allocation)
d['total_cu_upper_estimate']=sum(a['cu_upper_at_1_54_per_hour'] for a in d['allocations'])
d['notes']='Lifetime-based estimate, not exact billing. Shared account balance cannot isolate experiment CU. Additional allocation explicitly stopped. Budget compliance cannot be certified; estimate exceeds 5 CU.'
p.write_text(json.dumps(d,indent=2)+'\n')
(root/'results/current_allocation.json').write_text(json.dumps(allocation,indent=2)+'\n')
print(json.dumps(d,indent=2))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,4.5));ax.axis('off')
ax.text(.5,.84,'027r: STILL INCONCLUSIVE',ha='center',fontsize=20,weight='bold')
ax.text(.5,.61,'0 recovered validated pairs / 150 planned\nAccuracy, 95% CIs, McNemar p and tokens/s unavailable',ha='center',va='center',fontsize=13)
ax.text(.5,.31,'Prior scored artifacts lost; additional setup stopped before inference\nNo second scored round completed',ha='center',va='center',fontsize=12)
ax.text(.5,.12,f"L4 allocation-lifetime estimate: {d['total_cu_upper_estimate']:.3f} CU (budget: 5 CU)\nExact billed CU unavailable; budget compliance cannot be certified",ha='center',fontsize=11,color='#a33030')
fig.tight_layout();fig.savefig(root/'chart.png',dpi=180)
