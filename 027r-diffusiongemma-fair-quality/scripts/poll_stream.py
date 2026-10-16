from pathlib import Path
import subprocess
r=Path('/content/r027r')
print('setup:',(r/'status').read_text() if (r/'status').exists() else 'pending')
for f in ['/content/r027r/build.log','/content/patch_probe.log','/content/stream_build.log','/content/stream_pilot.log','/content/benchmark.log']:
 p=Path(f);print(p.name,p.read_text(errors='replace')[-1500:] if p.exists() else 'pending')
print('pilot files',list((r/'pilot').glob('*.meta.json')))
print('scored responses',len(list(r.glob('r*_*.meta.json'))))
