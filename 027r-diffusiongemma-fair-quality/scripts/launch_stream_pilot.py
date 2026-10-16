import subprocess,pathlib,base64
# File is staged from local script by the launch wrapper.
code="""import time,pathlib,subprocess,os
while not pathlib.Path('/content/r027r/stream_prompt.patch').exists():time.sleep(3)
e=dict(os.environ,PILOT='1',OFFLOAD='8')
subprocess.run(['python3','/content/stream_run.py','1'],env=e,check=True)
"""
subprocess.Popen(['python3','-c',code],stdout=open('/content/stream_pilot.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
print('Two-item pilot queued')
