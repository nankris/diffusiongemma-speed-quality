import os,time,json,subprocess,urllib.request,glob,re
from pathlib import Path
from decimal import Decimal,InvalidOperation
R=Path('/content/fair');R.mkdir(exist_ok=True)
B=Path('/content/llama.cpp/build/bin')
questions=json.load(open('/content/questions.json'))
# Same normalized user prompt in both arms; fresh chat for each item.
for q in questions:q['prompt']=q['prompt'].replace('\n',' ')
START=int(os.environ.get('START','0'));END=int(os.environ.get('END','150'))
Q=questions[START:END]
(R/f'prompts_{START}_{END}.txt').write_text('\n'.join(q['prompt'] for q in Q)+'\n')
from tokenizers import Tokenizer
tok=Tokenizer.from_file('/content/tokenizer.json')
def ntok(s):return len(tok.encode(s,add_special_tokens=False).ids)
def grade(s,gold):
 # Explicit final answer preferred; fallback to the final numerical mention.
 matches=re.findall(r'Answer:\s*\$?\s*([-+]?\d[\d,]*(?:\.\d+)?)',s,re.I)
 if not matches:matches=re.findall(r'[-+]?\d[\d,]*(?:\.\d+)?',s)
 v=matches[-1].replace(',','') if matches else None
 try:return int(Decimal(v)==Decimal(gold)),v
 except (InvalidOperation,TypeError):return 0,v
def save(arm,q,response,tokens_s,cap,raw):
 correct,pred=grade(response,q['gold'])
 row=dict(id=q['id'],arm=arm,correct=correct,prediction=pred,gold=q['gold'],response=response,tokens=ntok(response),tokens_s=tokens_s,cap_hit=cap,valid=True,raw=raw)
 with (R/'rows.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 return row
# DG native entropy-bound sampler; only template and input loop patched.
models={'dg':glob.glob('/content/m/dg/*.gguf')[0],'ar':glob.glob('/content/m/g4/*.gguf')[0]}
cmd=[str(B/'llama-diffusion-cli'),'-m',models['dg'],'-ngl','99','--n-cpu-moe','8','-n','4096','-t','2']
(R/f'dg_command_{START}.json').write_text(json.dumps(cmd))
outpath=R/f'dg_batch_{START}.jsonl'
env=dict(os.environ,FAIR_PROMPTS=str(R/f'prompts_{START}_{END}.txt'),FAIR_OUTPUT=str(outpath))
with (R/f'dg_{START}.out').open('w') as out,(R/f'dg_{START}.err').open('w') as err:
 p=subprocess.Popen(cmd,env=env,stdout=out,stderr=err)
 # Append completed items as they arrive so an interrupted run preserves evidence.
 done=0;t0=time.time()
 while p.poll() is None:
  if time.time()-t0>7200:p.kill();raise RuntimeError('DG timeout')
  if outpath.exists():
   lines=outpath.read_text().splitlines()
   for line in lines[done:]:
    d=json.loads(line);q=Q[d['index']];response=d['response'];n=ntok(response)
    save('dg',q,response,n/(d['elapsed_ms']/1000),d['blocks']>=16,d)
    done+=1;print('dg',START+done,flush=True)
  time.sleep(2)
 # collect last row
 if outpath.exists():
  for line in outpath.read_text().splitlines()[done:]:
   d=json.loads(line);response=d['response'];save('dg',Q[d['index']],response,ntok(response)/(d['elapsed_ms']/1000),d['blocks']>=16,d);done+=1
 if p.returncode or done!=len(Q):raise RuntimeError(f'DG failed code={p.returncode} rows={done}')
cmd=[str(B/'llama-server'),'-m',models['ar'],'-ngl','99','--n-cpu-moe','8','-c','6144','-np','1','-t','2','--port','8080','--host','127.0.0.1','--chat-template-kwargs','{"enable_thinking":false}']
(R/f'ar_command_{START}.json').write_text(json.dumps(cmd))
def api(route,data=None):
 req=urllib.request.Request('http://127.0.0.1:8080'+route,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req,timeout=300))
with (R/f'ar_{START}.out').open('w') as out,(R/f'ar_{START}.err').open('w') as err:
 p=subprocess.Popen(cmd,stdout=out,stderr=err)
 try:
  for _ in range(180):
   if p.poll() is not None:raise RuntimeError('AR server failed')
   try:api('/health');break
   except Exception:time.sleep(2)
  else:raise RuntimeError('AR server timeout')
  for i,q in enumerate(Q):
   msg=[dict(role='user',content=q['prompt'])]
   template=api('/apply-template',dict(messages=msg,add_generation_prompt=True,chat_template_kwargs=dict(enable_thinking=False)))
   prompt=template['prompt']
   if i==0:(R/f'ar_formatted_{START}.txt').write_text(prompt)
   d=api('/completion',dict(prompt=prompt,n_predict=4096,temperature=0,seed=2701,cache_prompt=False))
   response=d['content'];n=ntok(response)
   ms=d['timings']['predicted_ms']
   save('ar',q,response,n/(ms/1000),d.get('stop_type')=='limit' or d.get('tokens_predicted',0)>=4096,d)
   print('ar',START+i+1,flush=True)
 finally:
  p.terminate()
  try:p.wait(timeout=20)
  except subprocess.TimeoutExpired:p.kill();p.wait()
(R/f'complete_{START}_{END}').write_text('done')
