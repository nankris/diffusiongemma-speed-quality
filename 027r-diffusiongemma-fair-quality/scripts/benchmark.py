"""Run on dedicated Colab; each item is a fresh single-turn process."""
import json,time,pathlib,subprocess,glob,os,sys
ROOT=pathlib.Path('/content/r027r'); RAW=ROOT/'raw';RAW.mkdir(exist_ok=True)
items=json.load(open('/content/items.json'))
start=int(sys.argv[1]) if len(sys.argv)>1 else 0
end=int(sys.argv[2]) if len(sys.argv)>2 else 150
offload=int(os.environ.get('OFFLOAD','8'))
B='/content/llama.cpp/build/bin/'
for ix,item in enumerate(items[start:end],start):
 for arm in (['dg','ar'] if ix%2==0 else ['ar','dg']):
  stem=RAW/f'{ix:03}_{arm}'
  if stem.with_suffix('.json').exists(): continue
  if time.time()>float((ROOT/'deadline').read_text()): raise SystemExit('BUDGET_DEADLINE')
  model=glob.glob('/content/m/'+('dg' if arm=='dg' else 'g4')+'/*.gguf')[0]
  cmd=[B+('llama-diffusion-cli' if arm=='dg' else 'llama-completion'),'-m',model,'-ngl','99','--n-cpu-moe',str(offload),'-n','4096','-c','8192','-p',item['prompt']]
  if arm=='ar': cmd+=['-cnv','-st','--jinja','--temp','0','--reasoning','off']
  else: cmd+=['--seed',str(2701+ix)]
  t=time.time()
  with open(stem.with_suffix('.out'),'w') as out,open(stem.with_suffix('.err'),'w') as err:
   try: r=subprocess.run(cmd,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=150);code=r.returncode
   except subprocess.TimeoutExpired: code=124
  json.dump(dict(index=ix,id=item['id'],arm=arm,wall_s=time.time()-t,returncode=code,cmd=cmd),open(stem.with_suffix('.json'),'w'))
  if code: raise SystemExit(f'FAILED {ix} {arm} {code}')
 print(f'COMPLETE {ix+1}/{end}',flush=True)
print('ROUND_DONE',flush=True)
