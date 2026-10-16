import pathlib,subprocess
R=pathlib.Path('/content/r027r')
for name in ['status','probe.log','progress.log']:
 p=R/name
 print(name, p.read_text()[-1000:] if p.exists() else 'pending')
p=R/'build.log';print('build',p.read_text()[-600:] if p.exists() else 'pending')
print('complete arms',len(list((R/'raw').glob('*.json'))))
