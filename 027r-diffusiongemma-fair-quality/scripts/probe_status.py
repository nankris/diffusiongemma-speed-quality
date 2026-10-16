import pathlib,subprocess
R=pathlib.Path('/content/r027r')
for p in [R/'probe.log',*(R/'raw').glob('000_*')]:
 print(p.name,p.read_text()[-3500:])
print(subprocess.getoutput('free -h'))
