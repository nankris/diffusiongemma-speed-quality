import time,subprocess,pathlib
time.sleep(max(0,1792124631.0-time.time()))
p=subprocess.run(["colab","stop","-s","r5g027"],capture_output=True,text=True,timeout=90)
pathlib.Path('/workspace/work/tig/027r5-diffusiongemma-a100/results/watchdog_stop.txt').write_text(p.stdout+p.stderr)
