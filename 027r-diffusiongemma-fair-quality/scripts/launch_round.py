import subprocess,pathlib
r=1
subprocess.Popen(['python3','/content/run.py',str(r)],stdout=open('/content/benchmark.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
print('Round',r,'launched')
