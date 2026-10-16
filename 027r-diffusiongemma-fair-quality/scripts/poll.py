import subprocess
for c in ['cat /content/r027r/status','tail -5 /content/r027r/build.log','tail -15 /content/patch_probe.log','tail -3 /content/r027r/progress.txt','tail -5 /content/benchmark.log']:
 print(c);print(subprocess.getoutput(c))
