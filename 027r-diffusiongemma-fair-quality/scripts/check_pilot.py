import pathlib,subprocess
r=pathlib.Path('/content/r027r')
print(subprocess.getoutput("ps -eo pid,pgid,args | grep -E 'probe.py|patch_raw_prompt|llama-diffusion-cli|stream_run.py' | head -15"))
print('probe',pathlib.Path('/content/patch_probe.log').read_text()[-3000:])
print('pilot',pathlib.Path('/content/stream_pilot.log').read_text()[-3000:])
for f in (r/'pilot').glob('*.out'):print(f.name,f.read_text()[-1500:])
