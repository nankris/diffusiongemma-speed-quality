import json,os,time,subprocess,urllib.request,pathlib,sys
R=pathlib.Path('/content/current');B='/content/llama.cpp/build/bin/'
rd=int(sys.argv[1]);P=json.load(open('/content/prompts.json'))[(rd-1)*150:rd*150]
D=R/f'round{rd}';D.mkdir(exist_ok=True)
(D/'prompts.txt').write_text('\x1e'.join(p['rendered'] for p in P)+'\x1e')
def api(path,data=None):
 req=urllib.request.Request('http://127.0.0.1:8271'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req,timeout=240))
for arm in (['dg','ar'] if rd==1 else ['ar','dg']):
 model=next(pathlib.Path('/content/m/'+('dg' if arm=='dg' else 'g4')).glob('*.gguf'))
 cmd=[B+('llama-diffusion-cli' if arm=='dg' else 'llama-server'),'-m',str(model),'-ngl','99','--n-cpu-moe','8','-n','4096','-c','8192','-t','2']
 cmd+=['--no-conversation','--seed','27'] if arm=='dg' else ['--port','8271','--host','127.0.0.1','--parallel','1','--temp','0']
 (D/f'{arm}_command.json').write_text(json.dumps(cmd))
 with (D/f'{arm}.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdout=log,stderr=log,env=dict(os.environ,FAIR_INPUT=str(D/'prompts.txt'),FAIR_DIR=str(D)))
  try:
   if arm=='dg':
    if proc.wait(timeout=5400):raise RuntimeError('DG failed')
    if len(list(D.glob('dg_*.done')))!=len(P):raise RuntimeError('Missing DG outputs')
   else:
    for _ in range(240):
     if proc.poll() is not None:raise RuntimeError('AR exited')
     try:api('/health');break
     except Exception:time.sleep(1)
    else:raise TimeoutError('AR startup')
    for i,p in enumerate(P):
     if time.time()>float((R/'deadline').read_text()):raise TimeoutError('CU deadline')
     d=api('/completion',dict(prompt=p['rendered'],n_predict=4096,temperature=0,seed=27,cache_prompt=False))
     (D/f'ar_{i}.json').write_text(json.dumps(d))
     print(rd,arm,i+1,flush=True)
  finally:
   if proc.poll() is None:
    proc.terminate()
    try:proc.wait(timeout=15)
    except subprocess.TimeoutExpired:proc.kill();proc.wait()
 (D/f'{arm}_COMPLETE').touch()
(D/'COMPLETE').touch()
