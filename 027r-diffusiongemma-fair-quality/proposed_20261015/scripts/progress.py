from pathlib import Path
import subprocess
for p in ['/content/r027/status','/content/r027/build.log','/content/fair-build.exit','/content/fair-build.log','/content/bench.log']:
 q=Path(p);print(p, '\n'.join(q.read_text().splitlines()[-4:]) if q.exists() else 'pending')
q=Path('/content/fair/rows.jsonl')
if q.exists():
 import json,collections
 rows=[json.loads(x) for x in q.read_text().splitlines()];print('COUNTS',collections.Counter(r['arm'] for r in rows))
 for a in ['dg','ar']:
  rr=[r for r in rows if r['arm']==a]
  if rr:print(a,'n',len(rr),'correct',sum(r['correct'] for r in rr),'cap',sum(r['cap_hit'] for r in rr),'last',rr[-1]['response'][-300:])
print(subprocess.getoutput('nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader'))
