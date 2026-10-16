from pathlib import Path
import subprocess,os,signal,json,time
rows=[]
for line in subprocess.check_output(['ps','-eo','pid=,ppid=,args='],text=True).splitlines():
 p,pp,a=line.strip().split(None,2);rows.append((int(p),int(pp),a))
build=next((p,pp,a) for p,pp,a in rows if a.endswith('cmake --build build -j4 --target llama-diffusion-cli llama-server'))
parent=build[1];wrapper=next(pp for p,pp,a in rows if p==parent)
desc={wrapper}
while True:
 more={p for p,pp,a in rows if pp in desc};new=desc|more
 if new==desc:break
 desc=new
assert os.getpid() not in desc
# Kill the old setup wrapper first so it cannot write a false failure marker.
for p in [wrapper,parent]+list(desc-{wrapper,parent}):
 try:os.kill(p,signal.SIGKILL)
 except ProcessLookupError:pass
setup=Path('/content/setup.sh').read_text()
final=setup[setup.index("python - <<'META'"):]
Path('/content/finish_build.sh').write_text('''#!/bin/bash
set -euo pipefail
cd /content/llama.cpp
cmake --build build -j12 --target llama-diffusion-cli llama-server
'''+final)
subprocess.Popen(['bash','-c','bash /content/finish_build.sh >> /content/current/setup.log 2>&1; echo $? > /content/current/setup.exit'],start_new_session=True)
Path('/content/current/build_parallelism.json').write_text(json.dumps(dict(epoch=time.time(),old=4,new=12,cpu=os.cpu_count(),note='Incremental build restarted using all available CPUs; completed objects retained.')))
print('Incremental build resumed with 12 jobs; completed objects retained')
