import subprocess,time,pathlib,json,tarfile,sys,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];R=ROOT/'results';S=ROOT/'scripts';SESSION='tig027r-b';PYTHON=str(ROOT.parent/'.venv/bin/python')
def cli(args,timeout=150):
 p=subprocess.run(['colab']+args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(args)+': '+p.stdout[-1000:]+p.stderr[-1000:])
 return p.stdout

def execute(code,name):
 f=R/(name+'.py');f.write_text(code);return cli(['exec','-s',SESSION,'-f',str(f),'--timeout','60'],100)

def snapshot():
 out=cli(['exec','-s',SESSION,'-f',str(S/'remote_status.py'),'--timeout','45'],90)
 (R/'latest_status.txt').write_text(out);print(out,flush=True)
 cli(['download','-s',SESSION,'/content/current.tar.gz',str(R/'snapshot.tar.gz')],120)
 with tarfile.open(R/'snapshot.tar.gz') as t:t.extractall(R/'raw',filter='data')

def watchdog(start):
 script=R/'deadline_stop.py';script.write_text('import time,subprocess\ntime.sleep(max(0,'+str(start+180*60)+'-time.time()))\np=subprocess.run(["colab","stop","-s","'+SESSION+'"],capture_output=True,text=True)\nopen('+repr(str(R/'watchdog_stop.txt'))+',"w").write(p.stdout+p.stderr)\n')
 subprocess.Popen([sys.executable,str(script)],stdout=open(R/'watchdog.log','w'),stderr=subprocess.STDOUT,start_new_session=True)

while not (R/'allocated.json').exists():
 if (R/'allocation_finished.json').exists():raise SystemExit('No allocation: '+(R/'allocation_finished.json').read_text())
 time.sleep(5)
start=json.load(open(R/'allocated.json'))['start'];watchdog(start)
try:
 for name,remote in [('setup.sh','setup.sh'),('patch.py','patch.py'),('remote_run.py','remote_run.py')]:cli(['upload','-s',SESSION,str(S/name),'/content/'+remote])
 cli(['upload','-s',SESSION,str(ROOT.parent/'scripts/prompts.json'),'/content/prompts.json'])
 execute('import pathlib,subprocess,time\nR=pathlib.Path("/content/current");R.mkdir(exist_ok=True)\n(R/"deadline").write_text(str('+str(start+175*60)+'))\nprint(subprocess.getoutput("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"))\nsubprocess.Popen(["bash","-c","bash /content/setup.sh > /content/current/setup.log 2>&1; echo $? > /content/current/setup.exit"],start_new_session=True)\nprint("SETUP_LAUNCHED")','launch_setup')
 while True:
  time.sleep(35);snapshot()
  f=R/'raw/setup.exit'
  if f.exists():
   if f.read_text().strip()!='0':raise RuntimeError('Setup failed')
   break
  if time.time()>start+75*60:raise TimeoutError('Setup exceeded 75 minutes')
 for rd in [1,2]:
  execute('import subprocess\np=subprocess.Popen(["bash","-c","python /content/remote_run.py '+str(rd)+' > /content/current/run'+str(rd)+'.log 2>&1; echo $? > /content/current/run'+str(rd)+'.exit"],start_new_session=True)\nprint("ROUND_LAUNCHED",'+str(rd)+')','launch_round'+str(rd))
  while True:
   time.sleep(25)
   try:snapshot()
   except Exception as e:
    print('SNAPSHOT_RETRY',str(e),flush=True);time.sleep(5);snapshot()
   f=R/f'raw/run{rd}.exit'
   if f.exists():
    if f.read_text().strip()!='0':raise RuntimeError('Round failed')
    break
   if time.time()>start+173*60:raise TimeoutError('Budget deadline')
  subprocess.run([PYTHON,str(S/'analyze.py')],check=True,stdout=open(R/f'analysis_round{rd}.txt','w'))
  s=json.load(open(R/'summary.json'))[-1];print('LOOK',s,flush=True)
  if s['verdict']!='STILL INCONCLUSIVE':break
except Exception:
 (R/'failure.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
 try:snapshot()
 except Exception:pass
finally:
 out=subprocess.run(['colab','stop','-s',SESSION],capture_output=True,text=True,timeout=90)
 (R/'stop.txt').write_text(out.stdout+out.stderr)
 end=time.time();u=subprocess.run(['colab','usage'],capture_output=True,text=True,timeout=45);(R/'usage_after.txt').write_text(u.stdout+u.stderr)
 (R/'compute.json').write_text(json.dumps(dict(gpu='NVIDIA L4',start_epoch=start,stop_epoch=end,allocation_minutes=(end-start)/60,cu_estimate=(end-start)/3600*1.54,rate_cu_per_hour=1.54,exact_billed_cu=None,note='Shared account balance difference is not experiment-only usage; allocation lifetime estimate.'),indent=2))
 subprocess.run([PYTHON,str(S/'analyze.py')],stdout=open(R/'analysis_final.txt','w'),stderr=subprocess.STDOUT)
 (R/'FINISHED').touch()
