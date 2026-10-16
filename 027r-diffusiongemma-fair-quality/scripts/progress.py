import subprocess,pathlib
for p in ['status','build.log','probe.log','progress.log','ar_help.txt']:
 f=pathlib.Path('/content/r027r')/p
 if f.exists():
  s=f.read_text();print(p, '\n', '\n'.join(l for l in s.splitlines() if 'reason' in l) if p=='ar_help.txt' else s[-1000:])
print(subprocess.getoutput('find /content/r027r/raw -type f | wc -l'))
for p in pathlib.Path('/content/r027r/raw').glob('*'):
 if p.name.startswith('000_'): print(p.name,p.read_text()[-2500:])
