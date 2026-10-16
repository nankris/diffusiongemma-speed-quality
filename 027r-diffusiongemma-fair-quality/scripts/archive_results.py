import tarfile,pathlib
r=pathlib.Path('/content/r027r')
with tarfile.open('/content/027r-results.tar.gz','w:gz') as t:
 for p in r.iterdir():t.add(p,arcname=p.name)
print('Archive bytes',pathlib.Path('/content/027r-results.tar.gz').stat().st_size)
