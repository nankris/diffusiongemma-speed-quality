import pathlib,json,hashlib,urllib.request
root=pathlib.Path(__file__).resolve().parents[1]
url='https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl'
raw=urllib.request.urlopen(url).read();items=[json.loads(s) for s in raw.decode().splitlines()];p=json.load(open(root/'scripts/prompts.json'))
assert len(p)==300 and len(set(x['id'] for x in p))==300
for x in p:
 orig=items[x['id']];assert x['gold'].replace(',','')==orig['answer'].split('####')[-1].strip().replace(',','')
 assert x['prompt'].startswith(orig['question'])
 assert x['rendered']=='<|turn>user\n'+x['prompt']+'<turn|>\n<|turn>model\n<|channel>thought\n<channel|>'
(root/'results/input_validation.json').write_text(json.dumps(dict(n=300,unique_ids=300,gold_and_questions_match_public_source=True,source=url,source_sha256=hashlib.sha256(raw).hexdigest(),prompts_sha256=hashlib.sha256((root/'scripts/prompts.json').read_bytes()).hexdigest(),tokenizer_sha256=hashlib.sha256((root/'results/tokenizer.json').read_bytes()).hexdigest()),indent=2))
print('300 public questions, golds, and identical rendered prompts validated')
