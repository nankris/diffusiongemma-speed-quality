from pathlib import Path
import urllib.request,hashlib,json
r=Path(__file__).resolve().parents[1]
p=r/'results/tokenizer.json'
if not p.exists():p.write_bytes(urllib.request.urlopen('https://huggingface.co/unsloth/gemma-4-26B-A4B-it/resolve/main/tokenizer.json').read())
expected='cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f'
assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,'Tokenizer revision differs: retrieve matching original public revision'
print('tokenizer validated')
