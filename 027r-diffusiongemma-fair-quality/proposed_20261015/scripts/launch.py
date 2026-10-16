import subprocess
from pathlib import Path
cmd="while [ ! -f /content/fair-build.exit ]; do sleep 5; done; if [ \"$(cat /content/fair-build.exit)\" != 0 ]; then exit 1; fi; pip install -q tokenizers; python /content/bench.py > /content/bench.log 2>&1; echo $? > /content/bench.exit"
p=subprocess.Popen(['bash','-c',cmd],stdout=open('/content/launch.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
print('benchmark queued, PID',p.pid)
