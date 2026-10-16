import subprocess
subprocess.Popen("nohup bash -c 'while ! test -x /content/llama.cpp/build/bin/llama-server; do sleep 2; done; STAGE=pilot4 OFFLOAD=4 python /content/persistent.py 0 1 > /content/r027r/pilot4.log 2>&1' >/content/pilot_launcher.log 2>&1 &",shell=True)
print('persistent pilot queued')
