import subprocess,time,pathlib,json,tarfile,sys,traceback,re
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results';S=ROOT/'scripts';SESSION='r3027'
def cli(args,timeout=180):
 p=subprocess.run(['colab']+args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(args)+': '+p.stdout[-1000:]+p.stderr[-1000:])
 return p.stdout

def execute(code,name):
 f=R/(name+'.py');f.write_text(code);return cli(['exec','-s',SESSION,'-f',str(f),'--timeout','45'],90)

def snapshot():
 out=cli(['exec','-s',SESSION,'-f',str(S/'remote_status.py'),'--timeout','45'],90)
 (R/'latest_status.txt').write_text(out);print(out,flush=True)
 cli(['download','-s',SESSION,'/content/current.tar.gz',str(R/'snapshot.tmp.tar.gz')],120)
 (R/'snapshot.tmp.tar.gz').replace(R/'snapshot.tar.gz')
 with tarfile.open(R/'snapshot.tar.gz') as t:t.extractall(R/'raw',filter='data')
 # ACK only after successful local extraction of the completed batch.
 wait=R/'raw/WAITING'
 if wait.exists():
  label=wait.read_text();execute('from pathlib import Path\nPath("/content/current/ACK_'+label+'").touch()','ack')

start=json.load(open(R/'allocated.json'))['start'];rate=1.54;prior=json.load(open(R/'attempt1/compute.json'))['cu_estimate'];end_limit=start+(4.75-prior)/rate*3600
watch=R/'deadline_stop.py';watch.write_text('import time,subprocess\ntime.sleep(max(0,'+str(end_limit)+'-time.time()))\np=subprocess.run(["colab","stop","-s","r3027"],capture_output=True,text=True)\nopen('+repr(str(R/'watchdog_stop.txt'))+',"w").write(p.stdout+p.stderr)\n')
subprocess.Popen([sys.executable,str(watch)],stdout=open(R/'watchdog.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
try:
 for name in ['setup.sh','patch.py','remote_run.py','prompts.json']:cli(['upload','-s',SESSION,str(S/name),'/content/'+name])
 execute('import pathlib,subprocess\nR=pathlib.Path("/content/current");R.mkdir(exist_ok=True)\n(R/"deadline").write_text('+repr(str(end_limit-60))+')\nprint(subprocess.getoutput("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"))\nsubprocess.Popen(["bash","-c","bash /content/setup.sh > /content/current/setup.log 2>&1; echo $? > /content/current/setup.exit"],start_new_session=True)\nprint("SETUP_LAUNCHED")','launch_setup')
 while True:
  time.sleep(25)
  for retry in range(6):
   try:snapshot();break
   except Exception as e:
    print('SETUP_STATUS_RETRY',retry,str(e),flush=True)
    if retry==5:raise
    time.sleep(5)
  f=R/'raw/setup.exit'
  if f.exists():
   if f.read_text().strip()!='0':raise RuntimeError('Setup failed')
   break
  if time.time()>start+70*60:raise TimeoutError('Setup exceeded 70 minutes')
 execute('import subprocess\nsubprocess.Popen(["bash","-c","python /content/remote_run.py > /content/current/run.log 2>&1; echo $? > /content/current/run.exit"],start_new_session=True)\nprint("RUN_LAUNCHED")','launch_run')
 while True:
  time.sleep(20)
  try:snapshot()
  except Exception as e:
   print('SNAPSHOT_RETRY',str(e),flush=True);snapshot()
  f=R/'raw/run.exit'
  if f.exists():
   if f.read_text().strip()!='0':raise RuntimeError('Run failed')
   break
  if time.time()>end_limit-90:raise TimeoutError('Budget deadline')
except Exception:
 (R/'failure.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
 try:snapshot()
 except Exception:pass
finally:
 out=subprocess.run(['colab','stop','-s',SESSION],capture_output=True,text=True,timeout=90)
 (R/'stop.txt').write_text(out.stdout+out.stderr)
 end=time.time();u=subprocess.run(['colab','usage'],capture_output=True,text=True,timeout=45);(R/'usage_after.txt').write_text(u.stdout+u.stderr)
 (R/'compute.json').write_text(json.dumps(dict(gpu='NVIDIA L4',start_epoch=start,stop_epoch=end,allocation_minutes=(end-start)/60,cu_estimate=(end-start)/3600*rate+prior,current_allocation_cu=(end-start)/3600*rate,prior_allocation_cu=prior,rate_cu_per_hour=rate,exact_billed_cu=None,note='Allocation lifetime upper estimate; shared balance delta is not experiment-specific billing.'),indent=2))
 (R/'FINISHED').touch()
