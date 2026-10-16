import subprocess
subprocess.Popen("nohup bash /content/setup_l4.sh > /content/setup_l4.out 2>&1 &", shell=True)
print("launched")
