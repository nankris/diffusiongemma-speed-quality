import time,subprocess
time.sleep(max(0,1792120956.5721023-time.time()))
p=subprocess.run(["colab","stop","-s","r3027"],capture_output=True,text=True)
open('/workspace/work/tig/027r3-diffusiongemma-quality/results/watchdog_stop.txt',"w").write(p.stdout+p.stderr)
