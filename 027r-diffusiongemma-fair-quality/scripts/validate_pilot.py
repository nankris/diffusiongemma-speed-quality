import pathlib,re,json,subprocess
r=pathlib.Path('/content/r027r/pilot')
for p in r.glob('*.out'):
 if 'process' not in p.name:print(p.name,p.read_text()[-1800:])
for p in r.glob('*.api.json'):
 d=json.load(open(p));print(p.name,{k:d.get(k) for k in ['timings','truncated','stopped_limit','tokens_predicted','tokens_evaluated']})
print('GPU processes:',subprocess.getoutput('nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader'))
