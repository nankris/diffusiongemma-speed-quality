import subprocess,time,pathlib,json,tarfile,sys,traceback,os
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results';S=ROOT/'scripts';SESSION='r5g027'
def ledger(event,**kw):
 with (ROOT/'attempts.jsonl').open('a') as f:f.write(json.dumps(dict(epoch=time.time(),event=event,**kw))+'\n');f.flush();os.fsync(f.fileno())
def cli(args,timeout=90):
 p=subprocess.run(['colab']+args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(args)+': '+p.stdout[-1500:]+p.stderr[-1500:])
 return p.stdout
def execute(code,name):
 f=R/(name+'.py');f.write_text(code);return cli(['exec','-s',SESSION,'-f',str(f),'--timeout','30'],60)
def snapshot():
 out=cli(['exec','-s',SESSION,'-f',str(S/'remote_status.py'),'--timeout','30'],60);(R/'latest_status.txt').write_text(out);print(out,flush=True)
 cli(['download','-s',SESSION,'/content/current.tar.gz',str(R/'snapshot.tmp.tar.gz')],60);(R/'snapshot.tmp.tar.gz').replace(R/'snapshot.tar.gz')
 with tarfile.open(R/'snapshot.tar.gz') as t:t.extractall(R/'raw',filter='data')
 wait=R/'raw/WAITING'
 if wait.exists():
  label=wait.read_text();ledger('batch_saved',label=label);execute('from pathlib import Path\nPath("/content/current/ACK_'+label+'").touch()','ack');wait.unlink()
if (R/'FINISHED').exists():
 print('Already finished; analyze retained artifacts. No new allocation.');sys.exit(0)
if (R/'allocated.json').exists():
 state=json.load(open(R/'allocated.json'));start=state['start'];rate=state['rate_upper'];deadline=state['deadline']
else:
 start=float((R/'allocation_request_epoch').read_text())-15;rate=10.60;deadline=start+4.65/rate*3600
(R/'allocated.json').write_text(json.dumps(dict(start=start,session=SESSION,gpu='A100',rate_upper=rate,deadline=deadline)))
watch=R/'watchdog.py';watch.write_text('import time,subprocess,pathlib\ntime.sleep(max(0,'+str(deadline)+'-time.time()))\np=subprocess.run(["colab","stop","-s","r5g027"],capture_output=True,text=True,timeout=90)\npathlib.Path('+repr(str(R/'watchdog_stop.txt'))+').write_text(p.stdout+p.stderr)\n')
subprocess.Popen([sys.executable,str(watch)],stdout=open(R/'watchdog.log','a'),stderr=subprocess.STDOUT,start_new_session=True)
ledger('session_owned',session=SESSION,deadline=deadline)
try:
 for name in ['setup.sh','patch.py','remote_run.py','prompts.json']:cli(['upload','-s',SESSION,str(S/name),'/content/'+name])
 print(execute('import pathlib,subprocess\nR=pathlib.Path("/content/current");R.mkdir(exist_ok=True)\n(R/"deadline").write_text('+repr(str(deadline-45))+')\nprint(subprocess.getoutput("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"))\nif not (R/"setup.started").exists():\n (R/"setup.started").touch()\n subprocess.Popen(["bash","-c","bash /content/setup.sh > /content/current/setup.log 2>&1; echo $? > /content/current/setup.exit"],start_new_session=True)\nprint("SETUP_LAUNCHED")','launch_setup'),flush=True)
 while True:
  time.sleep(15)
  try:snapshot()
  except Exception as e:ledger('snapshot_retry',error=str(e));snapshot()
  f=R/'raw/setup.exit'
  if f.exists():
   if f.read_text().strip()!='0':raise RuntimeError('Setup failed')
   break
  if time.time()>min(start+1800,deadline-90):raise TimeoutError('Setup/load budget exhausted')
 print(execute('import subprocess,pathlib\nR=pathlib.Path("/content/current")\nif not (R/"run.started").exists():\n (R/"run.started").touch()\n subprocess.Popen(["bash","-c","python /content/remote_run.py > /content/current/run.log 2>&1; echo $? > /content/current/run.exit"],start_new_session=True)\nprint("RUN_LAUNCHED")','launch_run'),flush=True)
 while True:
  time.sleep(10)
  try:snapshot()
  except Exception as e:ledger('snapshot_retry',error=str(e));snapshot()
  f=R/'raw/run.exit'
  if f.exists():
   if f.read_text().strip()!='0':raise RuntimeError('Run failed')
   break
  if time.time()>deadline-80:raise TimeoutError('Budget deadline')
except Exception:
 (R/'failure.txt').write_text(traceback.format_exc());ledger('failure',error=traceback.format_exc());print(traceback.format_exc(),flush=True)
 try:snapshot()
 except Exception:pass
finally:
 p=subprocess.run(['colab','stop','-s',SESSION],capture_output=True,text=True,timeout=90);(R/'stop.txt').write_text(p.stdout+p.stderr);end=time.time()
 (R/'compute.json').write_text(json.dumps(dict(gpu='NVIDIA A100',start_epoch=start,stop_epoch=end,allocation_minutes=(end-start)/60,rate_cu_per_hour=rate,cu_upper_estimate=(end-start)/3600*rate,cu_estimate_at_inferred_rate=(end-start)/3600*5.30,exact_billed_cu=None,note='6 CU/hour conservative rate: two identical standard A100 sessions aggregate 10.60/h implies 5.30 each, with 13.2% buffer; experiment-only exact billing unavailable'),indent=2))
 ledger('stopped',output=p.stdout+p.stderr);(R/'FINISHED').touch()
