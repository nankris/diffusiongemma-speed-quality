import pathlib,json,time,datetime
r=pathlib.Path('/content/r027r')
for rd in [1,2]:
 a=[]
 for arm in ['dg','ar']:
  rows=[json.load(open(p)) for p in r.glob(f'r{rd}_{arm}_*.meta.json')]
  a.append(f'{arm} {len(rows)}/150 (mean {sum(x["wall_s"] for x in rows)/len(rows):.1f}s)' if rows else f'{arm} 0/150')
 print('round',rd,', '.join(a),'DONE' if (r/f'ROUND{rd}_DONE').exists() else '')
p=pathlib.Path('/content/benchmark.log')
if p.exists() and p.stat().st_size:print(p.read_text()[-1600:])
print('deadline minutes left',round((float((r/'recovery_deadline').read_text())-time.time())/60,1))
