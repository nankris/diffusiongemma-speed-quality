"""Validate fixed input order, response identities, and synchronization ledger."""
from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1]
source=[json.loads(x) for x in (r/'results/gsm8k_test.jsonl').read_text().splitlines()]
p=json.load(open(r/'scripts/prompts.json'));assert len(p)==200
for i,x in enumerate(p):
 assert x['id']==i and x['prompt'].startswith(source[i]['question'])
 assert x['gold']==source[i]['answer'].split('####')[-1].strip()
 assert x['rendered']=='<|turn>user\n'+x['prompt']+'<turn|>\n<|turn>model\n<|channel>thought\n<channel|>'
counts={}
for arm in ['ar','dg']:
 fs=list((r/'results/raw/answers').glob(arm+'_*.json'));counts[arm]=len(fs)
 for f in fs:
  d=json.load(open(f));assert d['id']==d['index'] and 0<=d['id']<200
jf=r/'results/raw/answers.jsonl'
if jf.exists():
 rows=[json.loads(x) for x in jf.read_text().splitlines()]
 ids=[(x['arm'],x['index']) for x in rows]
 assert len(ids)==len(set(ids)), 'Duplicate JSONL response'
 if counts=={'ar':200,'dg':200}:
  assert ids==[('ar',i) for i in range(200)]+[('dg',i) for i in range(200)], 'AR-first execution order violated'
entries=[json.loads(x) for x in (r/'attempts.jsonl').read_text().splitlines()]
print(json.dumps(dict(input_order_validated=True,responses=counts,saved_batches=[x['label'] for x in entries if x['event']=='batch_saved'],tokenizer_sha256=hashlib.sha256((r/'results/tokenizer.json').read_bytes()).hexdigest()),indent=2))
