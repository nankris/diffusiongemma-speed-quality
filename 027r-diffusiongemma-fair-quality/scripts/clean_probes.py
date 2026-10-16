import pathlib,os,signal,subprocess,time
killed=[]
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  args=p.read_bytes().split(b'\0');pid=int(p.parent.name)
  if pid==os.getpid():continue
  match=(len(args)>1 and args[1]==b'/content/patch_raw_prompt.py') or (len(args)>2 and args[1]==b'-c' and b'/content/probe.py' in args[2] and b'ALL_SETUP_DONE' in args[2])
  if match:
   g=os.getpgid(pid)
   if g!=os.getpgrp():os.killpg(g,signal.SIGTERM);killed.append(pid)
 except (ProcessLookupError,PermissionError,FileNotFoundError):pass
print('Stopped superseded probe groups:',killed)
print(subprocess.getoutput('nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader'))
