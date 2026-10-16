import json, random, urllib.request
from pathlib import Path
url='https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl'
raw=urllib.request.urlopen(url).read()
items=[json.loads(x) for x in raw.splitlines()]
indices=random.Random(2701).sample(range(len(items)),500)
rows=[dict(id=i,question=items[i]['question'],gold=items[i]['answer'].split('####')[-1].strip(),prompt=items[i]['question']+'\nSolve the problem. End with Answer: <number>.') for i in indices]
Path('027r-diffusiongemma-fair-quality/results/questions.json').write_text(json.dumps(rows,indent=2))
import hashlib
print(len(rows),hashlib.sha256(raw).hexdigest())
