import json,os,time,subprocess,urllib.request,pathlib
R=pathlib.Path('/content/current');B='/content/llama.cpp/build/bin/'
P=json.load(open('/content/prompts.json'))[:300]
D=R/'answers';D.mkdir(exist_ok=True)
def api(path,data=None):
 req=urllib.request.Request('http://127.0.0.1:8271'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req,timeout=240))
def barrier(label):
 (R/'WAITING').write_text(label)
 while not (R/('ACK_'+label)).exists():
  if time.time()>float((R/'deadline').read_text()):raise TimeoutError('Budget deadline during sync')
  time.sleep(1)
 (R/'WAITING').unlink(missing_ok=True)
for arm in ['dg','ar']:
 model=next(pathlib.Path('/content/m/'+('dg' if arm=='dg' else 'g4')).glob('*.gguf'))
 if all((D/f'{arm}_{i}.json').exists() for i in range(300)):continue
 cmd=[B+('llama-diffusion-cli' if arm=='dg' else 'llama-server'),'-m',str(model),'-ngl','99','--n-cpu-moe','8','-n','4096','-c','8192','-t','2']
 cmd+=['--no-conversation','--seed','27'] if arm=='dg' else ['--port','8271','--host','127.0.0.1','--parallel','1','--temp','0']
 (R/f'{arm}_command.json').write_text(json.dumps(cmd))
 with (R/f'{arm}.log').open('a') as log:
  if arm=='dg':
   # FIFO keeps the model resident; send at most 25 new prompts before a local-sync acknowledgement.
   fifo=R/'input.fifo';fifo.unlink(missing_ok=True);os.mkfifo(fifo)
   proc=subprocess.Popen(cmd,stdout=log,stderr=log,env=dict(os.environ,FAIR_INPUT=str(fifo),FAIR_DIR=str(D)))
  else:
   proc=subprocess.Popen(cmd,stdout=log,stderr=log)
  try:
   if arm=='dg':
    while True:
     try:fd=os.open(fifo,os.O_WRONLY|os.O_NONBLOCK);break
     except OSError:
      if proc.poll() is not None:raise RuntimeError('DG exited before FIFO startup')
      if time.time()>float((R/'deadline').read_text()):raise TimeoutError('DG startup budget')
      time.sleep(.5)
    os.set_blocking(fd,True)
    with os.fdopen(fd,'w') as out:
     seq=0
     for start in range(0,300,25):
      todo=[i for i in range(start,start+25) if not (D/f'dg_{i}.json').exists()]
      for i in todo:
       # C++ filenames index only newly issued prompts; avoid collisions on resume.
       for ext in ['out','done','ms']:(D/f'dg_{seq}.{ext}').unlink(missing_ok=True)
       out.write(P[i]['rendered']+'\x1e');out.flush()
       while not (D/f'dg_{seq}.done').exists():
        if proc.poll() is not None:raise RuntimeError('DG exited')
        if time.time()>float((R/'deadline').read_text()):raise TimeoutError('Budget deadline')
        time.sleep(.2)
       d=dict(index=i,id=P[i]['id'],text=(D/f'dg_{seq}.out').read_text(),milliseconds=float((D/f'dg_{seq}.ms').read_text()),steps_blocks=(D/f'dg_{seq}.done').read_text())
       target=D/f'dg_{i}.json';tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(d));tmp.replace(target)
       seq+=1
      barrier(f'dg_{start+25}')
   else:
    for _ in range(240):
     if proc.poll() is not None:raise RuntimeError('AR exited')
     try:api('/health');break
     except Exception:time.sleep(1)
    else:raise TimeoutError('AR startup')
    for start in range(0,300,25):
     for i in range(start,start+25):
      target=D/f'ar_{i}.json'
      if target.exists():continue
      if time.time()>float((R/'deadline').read_text()):raise TimeoutError('Budget deadline')
      d=api('/completion',dict(prompt=P[i]['rendered'],n_predict=4096,temperature=0,seed=27,cache_prompt=False))
      d.update(index=i,id=P[i]['id']);tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(d));tmp.replace(target)
     barrier(f'ar_{start+25}')
  finally:
   if proc.poll() is None:
    proc.terminate()
    try:proc.wait(timeout=15)
    except subprocess.TimeoutExpired:proc.kill();proc.wait()
 (R/f'{arm}_COMPLETE').touch()
(R/'COMPLETE').touch()
