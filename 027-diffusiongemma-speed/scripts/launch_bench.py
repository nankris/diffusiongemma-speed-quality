import subprocess
subprocess.Popen("cd /content && nohup bash /content/bench.sh > /content/bench.out 2>&1 &", shell=True)
print("launched")
