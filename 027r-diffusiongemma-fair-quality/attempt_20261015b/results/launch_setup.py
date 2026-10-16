import pathlib,subprocess,time
R=pathlib.Path("/content/current");R.mkdir(exist_ok=True)
(R/"deadline").write_text(str(1792059334.4679475))
print(subprocess.getoutput("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"))
subprocess.Popen(["bash","-c","bash /content/setup.sh > /content/current/setup.log 2>&1; echo $? > /content/current/setup.exit"],start_new_session=True)
print("SETUP_LAUNCHED")