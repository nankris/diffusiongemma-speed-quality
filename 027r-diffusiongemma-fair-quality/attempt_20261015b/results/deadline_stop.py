import time,subprocess
time.sleep(max(0,1792059634.4679475-time.time()))
p=subprocess.run(["colab","stop","-s","tig027r-b"],capture_output=True,text=True)
open('/workspace/work/tig/027r-diffusiongemma-fair-quality/attempt_20261015b/results/watchdog_stop.txt',"w").write(p.stdout+p.stderr)
