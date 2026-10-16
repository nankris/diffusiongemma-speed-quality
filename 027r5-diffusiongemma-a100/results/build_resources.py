import os,subprocess
print('CPU',os.cpu_count())
print(subprocess.getoutput('free -m'))
print(subprocess.getoutput("ps -eo pid,ppid,comm,args | grep -E 'cmake --build|gmake|make -|nvcc' | head -12"))
