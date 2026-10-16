import pathlib,subprocess
R=pathlib.Path("/content/current");R.mkdir(exist_ok=True)
(R/"deadline").write_text('1792124586.0')
print(subprocess.getoutput("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"))
if not (R/"setup.started").exists():
 (R/"setup.started").touch()
 subprocess.Popen(["bash","-c","bash /content/setup.sh > /content/current/setup.log 2>&1; echo $? > /content/current/setup.exit"],start_new_session=True)
print("SETUP_LAUNCHED")