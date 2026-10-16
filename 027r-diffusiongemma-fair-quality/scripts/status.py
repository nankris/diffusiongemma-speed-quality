import subprocess
print(subprocess.getoutput('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader'))
print(subprocess.getoutput('cat /content/r027r/status; tail -8 /content/r027r/build.log; tail -4 /content/r027r/dl_dg.log; tail -4 /content/r027r/dl_g4.log'))
