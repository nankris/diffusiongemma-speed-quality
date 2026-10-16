"""Persistent native DG CLI and AR server; single-turn prompts, no history."""
import pathlib,json,time,subprocess,glob,os,sys,select,urllib.request,urllib.error
R=pathlib.Path('/content/r027r');B='/content/llama.cpp/build/bin/'
start=int(sys.argv[1]);end=int(sys.argv[2]);offload=int(os.environ.get('OFFLOAD','4'));stage=os.environ.get('STAGE','raw')
RAW=R/stage;RAW.mkdir(exist_ok=True)
tag=f'{stage}_{start}_{end}'
items=json.load(open('/content/items.json'))
def budget():
 if time.time()>float((R/'deadline').read_text()):raise TimeoutError('BUDGET_DEADLINE')
def read_prompt(proc,timeout=180):
 data=b'';deadline=time.time()+timeout
 while not data.endswith(b'\n> '):
  budget()
  if time.time()>deadline:raise TimeoutError('DG response timeout')
  ready,_,_=select.select([proc.stdout],[],[],1)
  if ready:
   chunk=os.read(proc.stdout.fileno(),65536)
   if not chunk:raise RuntimeError('DG exited '+str(proc.poll()))
   data+=chunk
 return data.decode(errors='replace')[:-3]
def request(path,data=None):
 req=urllib.request.Request('http://127.0.0.1:8270'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req,timeout=150))
for arm in (['dg','ar'] if start==0 else ['ar','dg']):
 model=glob.glob('/content/m/'+('dg' if arm=='dg' else 'g4')+'/*.gguf')[0]
 base=['-m',model,'-ngl','99','--n-cpu-moe',str(offload),'-n','4096','-c','6144']
 cmd=[B+('llama-diffusion-cli' if arm=='dg' else 'llama-server')]+base
 cmd+=['-cnv','--seed','2701'] if arm=='dg' else ['--port','8270','--host','127.0.0.1','--parallel','1','--temp','0','--reasoning','off']
 with open(R/f'{tag}_{arm}_process.err','w') as err,open(R/f'{tag}_{arm}_process.out','w') as out:
  t=time.time();proc=subprocess.Popen(cmd,stdin=subprocess.PIPE if arm=='dg' else subprocess.DEVNULL,stdout=subprocess.PIPE if arm=='dg' else out,stderr=err)
  try:
   if arm=='dg':initial=read_prompt(proc);out.write(initial);out.flush()
   else:
    while True:
     budget()
     if proc.poll() is not None:raise RuntimeError('AR server exited '+str(proc.returncode))
     try:request('/health');break
     except (urllib.error.URLError,TimeoutError):time.sleep(1)
   json.dump({'cmd':cmd,'startup_s':time.time()-t},open(R/f'{tag}_{arm}_startup.json','w'),indent=2)
   for ix in range(start,end):
    budget();item=items[ix];prompt=item['prompt'].replace('\n',' ');stem=RAW/f'{ix:03}_{arm}'
    t=time.time();err_offset=(R/f'{tag}_{arm}_process.err').stat().st_size
    if arm=='dg':
     if ix>start:
      proc.stdin.write(b'/clear\n');proc.stdin.flush();out.write(read_prompt(proc))
     proc.stdin.write((prompt+'\n').encode());proc.stdin.flush();response=read_prompt(proc)
     out.write(response);out.flush();stem.with_suffix('.out').write_text(response)
    else:
     formatted='<|turn>user\n'+prompt+'<turn|>\n<|turn>model\n<|channel>thought\n<channel|>'
     data=request('/completion',dict(prompt=formatted,n_predict=4096,temperature=0,seed=2701+ix,cache_prompt=False))
     json.dump(data,open(stem.with_suffix('.api.json'),'w'),indent=2)
     stem.with_suffix('.out').write_text(data['content'])
    with open(R/f'{tag}_{arm}_process.err','rb') as log:
     log.seek(err_offset);err_data=log.read().decode(errors='replace')
    stem.with_suffix('.err').write_text(err_data)
    json.dump(dict(index=ix,id=item['id'],arm=arm,wall_s=time.time()-t,returncode=0,cmd=cmd,prompt=prompt),open(stem.with_suffix('.json'),'w'),indent=2)
    print(f'COMPLETE {arm} {ix+1}/{end}',flush=True)
  finally:
   proc.terminate()
   try:proc.wait(timeout=15)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
print('ROUND_DONE',flush=True)
