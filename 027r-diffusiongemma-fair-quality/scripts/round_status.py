from pathlib import Path
import json,time
R=Path('/content/r027r')
for p in R.glob('round_*.log'):print(p.name,p.read_text()[-500:])
for arm in ['dg','ar']:
 meta=[json.load(open(p)) for p in (R/'raw').glob(f'*_{arm}.json') if '.api.' not in p.name]
 print(arm,'completed',len(meta),'mean wall',round(sum(v['wall_s'] for v in meta)/len(meta),2) if meta else None)
print('deadline remaining min',round((float((R/'deadline').read_text())-time.time())/60,1))
