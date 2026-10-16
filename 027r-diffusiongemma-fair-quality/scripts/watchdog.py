"""Local backup cleanup for this experiment's session only."""
import datetime,time,pathlib,subprocess
root=pathlib.Path(__file__).resolve().parents[1]
deadline=datetime.datetime.fromisoformat('2026-10-15T02:59:00+00:00').timestamp()
while time.time()<deadline:
 if (root/'results/session_stopped.json').exists():raise SystemExit('Session already stopped')
 time.sleep(min(30,max(0,deadline-time.time())))
r=subprocess.run(['colab','stop','-s','tig027r'],capture_output=True,text=True)
(root/'results/watchdog_stop.txt').write_text(r.stdout+r.stderr)
