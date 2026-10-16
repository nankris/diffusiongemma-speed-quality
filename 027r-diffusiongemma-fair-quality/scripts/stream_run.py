import pathlib,json,time,subprocess,select,os,urllib.request,urllib.error,sys
R=pathlib.Path('/content/r027r'); B='/content/llama.cpp/build/bin/'
rd=int(sys.argv[1]);items=[p for p in json.load(open('/content/prompts.json')) if p['round']==rd];offload=int(os.environ.get('OFFLOAD','8'))
deadline=float((R/'recovery_deadline').read_text())
if rd==2:items=items[:150]
if os.environ.get('PILOT'):
 items=items[:2];R=R/'pilot';R.mkdir(exist_ok=True)
def check():
 if time.time()>deadline:raise TimeoutError('Experiment CU deadline')
def read_turn(proc,timeout=180):
 data=b'';end=time.time()+timeout
 while not data.endswith(b'\n> '):
  check()
  if time.time()>end:raise TimeoutError('DG response timeout')
  if select.select([proc.stdout],[],[],1)[0]:
   b=os.read(proc.stdout.fileno(),65536)
   if not b:raise RuntimeError('DG exited '+str(proc.poll()))
   data+=b
 return data.decode(errors='replace')[:-3]
def request(path,data=None):
 req=urllib.request.Request('http://127.0.0.1:8271'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req,timeout=180))
for arm in (['dg','ar'] if rd==1 else ['ar','dg']):
 model=next(pathlib.Path('/content/m/'+('dg' if arm=='dg' else 'g4')).glob('*.gguf'))
 cmd=[B+('llama-diffusion-cli' if arm=='dg' else 'llama-server'),'-m',str(model),'-ngl','99','--n-cpu-moe',str(offload),'-n','4096','-c','8192']
 if arm=='ar':cmd+=['--port','8271','--host','127.0.0.1','--parallel','1','--temp','0']
 else:cmd+=['--no-conversation','--seed','27']
 with open(R/f'round{rd}_{arm}_process.err','w') as err,open(R/f'round{rd}_{arm}_process.out','w') as out:
  t=time.time();proc=subprocess.Popen(cmd,stdin=subprocess.PIPE if arm=='dg' else subprocess.DEVNULL,stdout=subprocess.PIPE if arm=='dg' else out,stderr=err)
  try:
   if arm=='dg':out.write(read_turn(proc));out.flush()
   else:
    while True:
     check()
     if proc.poll() is not None:raise RuntimeError('AR server exited '+str(proc.returncode))
     try:request('/health');break
     except (urllib.error.URLError,TimeoutError):time.sleep(1)
   json.dump({'cmd':cmd,'startup_s':time.time()-t},open(R/f'round{rd}_{arm}_startup.json','w'),indent=2)
   for p in items:
    check();stem=R/f"r{rd}_{arm}_{p['id']}";t=time.time();offset=(R/f'round{rd}_{arm}_process.err').stat().st_size
    if arm=='dg':
     proc.stdin.write((p['rendered']+'\x1e').encode());proc.stdin.flush();reply=read_turn(proc);stem.with_suffix('.out').write_text(reply);out.write(reply);out.flush()
    else:
     data=request('/completion',{'prompt':p['rendered'],'n_predict':4096,'temperature':0,'seed':27,'cache_prompt':False})
     json.dump(data,open(stem.with_suffix('.api.json'),'w'),indent=2);stem.with_suffix('.out').write_text(data['content'])
    with open(R/f'round{rd}_{arm}_process.err','rb') as f:f.seek(offset);stem.with_suffix('.err').write_text(f.read().decode(errors='replace'))
    json.dump({'id':p['id'],'round':rd,'arm':arm,'wall_s':time.time()-t,'exit_code':0,'prompt':p['rendered']},open(stem.with_suffix('.meta.json'),'w'),indent=2)
    with open(R/'progress.txt','a') as f:f.write(f'{rd} {arm} {p["id"]} done\n')
  finally:
   proc.terminate()
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
(R/f'ROUND{rd}_DONE').touch();print('ROUND_DONE',rd,flush=True)
