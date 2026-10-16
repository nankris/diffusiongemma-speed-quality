import subprocess,time,pathlib,json,re
R=pathlib.Path(__file__).resolve().parents[1]/'results'
# First refusal already happened at 06:57 UTC. Five full minutes before retry.
time.sleep(300)
for retry in range(1,7):
 usage=subprocess.run(['colab','usage'],capture_output=True,text=True)
 (R/f'usage_retry{retry}.txt').write_text(usage.stdout+usage.stderr)
 m=re.search(r'Current balance: ([\d.]+)',usage.stdout)
 if usage.returncode or not m or float(m[1])<158.4:
  (R/'allocation_finished.json').write_text(json.dumps(dict(status='budget_or_usage_block',retry=retry)));break
 out=subprocess.run(['colab','new','--gpu','L4','-s','tig027r-b'],capture_output=True,text=True)
 (R/f'allocation_retry{retry}.txt').write_text(out.stdout+out.stderr)
 if out.returncode==0:
  (R/'allocated.json').write_text(json.dumps(dict(start=time.time(),retry=retry)));break
 if retry<6:time.sleep(300)
else:(R/'allocation_finished.json').write_text(json.dumps(dict(status='refused_after_six_retries')))
