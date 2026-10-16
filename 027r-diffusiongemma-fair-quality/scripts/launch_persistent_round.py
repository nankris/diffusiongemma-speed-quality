import subprocess,os
start=os.environ.get('START','0');end=os.environ.get('END','150')
subprocess.Popen(f'nohup env STAGE=raw OFFLOAD=8 python /content/persistent.py {start} {end} > /content/r027r/round_{start}_{end}.log 2>&1 &',shell=True)
print('scored round launched',start,end)
