import pathlib,subprocess,time
p=pathlib.Path('/content/r027r/status')
script="""import pathlib,time,subprocess
p=pathlib.Path('/content/r027r/status')
while not (p.exists() and 'ALL_SETUP_DONE' in p.read_text()):time.sleep(5)
r=subprocess.run(['python3','/content/probe.py'],stdout=open('/content/probe.log','w'),stderr=subprocess.STDOUT)
"""
subprocess.Popen(['python3','-c',script],start_new_session=True,stdout=open('/content/wait.log','w'),stderr=subprocess.STDOUT)
print('Probe queued after setup')
