import pathlib,subprocess
R=pathlib.Path("/content/current");R.mkdir(exist_ok=True)
(R/"deadline").write_text('1792120896.5721023')
print(subprocess.getoutput("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"))
subprocess.Popen(["bash","-c","bash /content/setup.sh > /content/current/setup.log 2>&1; echo $? > /content/current/setup.exit"],start_new_session=True)
print("SETUP_LAUNCHED")