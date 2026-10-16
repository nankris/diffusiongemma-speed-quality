import subprocess
for c in ['tail -30 /content/setup.out','ps -eo pid,etime,args | head -35','ls -lh /content/r027r /content/llama.cpp /content/m/dg']:
 print(c); print(subprocess.getoutput(c))
