import subprocess
print(subprocess.getoutput('tail -15 /content/setup.out'))
print(subprocess.getoutput('ps -eo pid,etime,args | tail -15'))
