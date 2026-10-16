import subprocess
subprocess.Popen("nohup bash -c 'bash /content/setup_l4_dgonly.sh > /content/setup.out 2>&1; bash /content/bench_run2_dg.sh > /content/bench2dg.out 2>&1' > /dev/null 2>&1 &", shell=True)
print("launched")
