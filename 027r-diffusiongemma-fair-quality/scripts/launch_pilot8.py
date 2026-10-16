import subprocess
subprocess.Popen('nohup env STAGE=pilot8 OFFLOAD=8 python /content/persistent.py 0 1 > /content/r027r/pilot8.log 2>&1 &',shell=True)
print('persistent pilot8 launched')
