import subprocess
subprocess.Popen("cd /content && nohup bash /content/bench_run2.sh > /content/bench2.out 2>&1 &", shell=True)
print("launched")
