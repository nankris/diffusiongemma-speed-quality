import subprocess,pathlib
R=pathlib.Path("/content/current")
if not (R/"run.started").exists():
 (R/"run.started").touch()
 subprocess.Popen(["bash","-c","python /content/remote_run.py > /content/current/run.log 2>&1; echo $? > /content/current/run.exit"],start_new_session=True)
print("RUN_LAUNCHED")