import subprocess
subprocess.Popen(['bash','/content/setup.sh'],stdout=open('/content/setup.out','w'),stderr=subprocess.STDOUT,start_new_session=True)
print('Setup launched')
