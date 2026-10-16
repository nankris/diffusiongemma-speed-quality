import subprocess,pathlib,json,time
p=pathlib.Path('/content/r027r')
print(subprocess.getoutput('cat /content/r027r/status; tail -6 /content/r027r/build.log'))
if (p/'status').exists() and 'ALL_SETUP_DONE' in (p/'status').read_text():
 q=json.load(open('/content/prompts.json'))[0]
 for arm,sub in [('dg','dg'),('ar','g4')]:
  cmd=['/content/llama.cpp/build/bin/'+('llama-diffusion-cli' if arm=='dg' else 'llama-completion'),'-m',str(next(pathlib.Path('/content/m/'+sub).glob('*.gguf'))),'-ngl','99','--n-cpu-moe','4','-c','8192','-n','4096','--in-prefix','','--no-conversation','--no-display-prompt','-p',q['rendered']]
  if arm=='dg':
   cmd.remove('--in-prefix');cmd.remove('');cmd.remove('--no-display-prompt')
  if arm=='ar':cmd+=['--temp','0','--seed','27']
  t=time.time();r=subprocess.run(cmd,stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=150)
  (p/f'probe_{arm}.out').write_text(r.stdout);(p/f'probe_{arm}.err').write_text(r.stderr)
  print(arm,r.returncode,time.time()-t,r.stdout[-4000:],r.stderr[-2000:])
