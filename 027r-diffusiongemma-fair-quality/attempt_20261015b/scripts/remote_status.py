import pathlib,subprocess,json,tarfile
R=pathlib.Path('/content/current')
print(subprocess.getoutput('nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv,noheader'))
for p in ['setup.log','run1.log','run2.log']:
 q=R/p
 if q.exists():print(p,q.read_text(errors='replace')[-1500:])
for rd in [1,2]:
 D=R/f'round{rd}'
 if D.exists():print('ROUND',rd,'DG',len(list(D.glob('dg_*.done'))),'AR',len(list(D.glob('ar_*.json'))),'COMPLETE',(D/'COMPLETE').exists())
with tarfile.open('/content/current.tar.gz','w:gz') as t:
 for p in R.rglob('*'):
  if p.is_file():t.add(p,arcname=str(p.relative_to(R)))
print('ARCHIVE_READY')
