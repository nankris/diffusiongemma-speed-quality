from pathlib import Path
R=Path('/content/r027r')
for name in ['server_build.log','pilot8.log','raw.log','pilot8_dg_process.err','pilot8_ar_process.err']:
 p=R/name;print(name,p.read_text()[-1200:] if p.exists() else 'pending')
for p in (R/'pilot8').glob('*.out'): print(p.name,p.read_text()[-1800:])
print('raw arms',len(list((R/'raw').glob('*.json'))))
