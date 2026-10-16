import json, subprocess, time, pathlib, sys
P=pathlib.Path('/content/r027r'); P.mkdir(exist_ok=True)
round_no=int(sys.argv[1]); rows=[p for p in json.load(open('/content/prompts.json')) if p['round']==round_no]
# Both engines receive byte-identical rendered non-thinking prompts. Each engine adds its own BOS.
for arm in ['dg','ar']:
 model=next(pathlib.Path('/content/m/'+('dg' if arm=='dg' else 'g4')).glob('*.gguf'))
 for p in rows:
  stem=P/f"r{round_no}_{arm}_{p['id']}"
  if stem.with_suffix('.meta.json').exists():continue
  cmd=['/content/llama.cpp/build/bin/'+('llama-diffusion-cli' if arm=='dg' else 'llama-completion'),'-m',str(model),'-ngl','99','--n-cpu-moe','4','-c','8192','-n','4096','--in-prefix','','--no-conversation','--no-display-prompt','-p',p['rendered']]
  if arm=='dg':
   cmd.remove('--in-prefix');cmd.remove('');cmd.remove('--no-display-prompt')
  if arm=='ar':cmd+=['--temp','0','--seed','27']
  start=time.time()
  try:
   with open(stem.with_suffix('.out'),'w') as o,open(stem.with_suffix('.err'),'w') as e:
    r=subprocess.run(cmd,stdin=subprocess.DEVNULL,stdout=o,stderr=e,timeout=180)
   code=r.returncode
  except subprocess.TimeoutExpired:code=124
  json.dump({'id':p['id'],'arm':arm,'round':round_no,'wall_s':time.time()-start,'exit_code':code},open(stem.with_suffix('.meta.json'),'w'))
  with open(P/'progress.txt','a') as f:f.write(f'{round_no} {arm} {p["id"]} exit={code}\n')
  if code:raise RuntimeError(f'Failed {stem}: {code}')
(P/f'ROUND{round_no}_DONE').touch()
