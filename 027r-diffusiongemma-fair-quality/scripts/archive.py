import subprocess
print(subprocess.getoutput('tar -czf /content/r027r.tar.gz -C /content r027r'))
print('archive ready')
