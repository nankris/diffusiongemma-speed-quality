import pathlib,subprocess,tarfile
R=pathlib.Path('/content/current')
print(subprocess.getoutput('nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv,noheader'))
for name in ['setup.log','run.log','dg.log','ar.log']:
 p=R/name
 if p.exists():print(name,p.read_text(errors='replace')[-600:])
for arm in ['dg','ar']:print(arm,len(list((R/'answers').glob(arm+'_*.json'))))
with tarfile.open('/content/current.tar.gz','w:gz') as t:
 for p in R.rglob('*'):
  if p.is_file():t.add(p,arcname=str(p.relative_to(R)))
print('ARCHIVE_READY')
