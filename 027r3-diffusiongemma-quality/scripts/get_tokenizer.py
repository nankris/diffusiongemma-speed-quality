from huggingface_hub import hf_hub_download
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
p=hf_hub_download('unsloth/gemma-4-26B-A4B-it',filename='tokenizer.json')
shutil.copyfile(p,root/'results/tokenizer.json')

import hashlib,json
expected=json.load(open(root/'results/input_validation.json'))['tokenizer_sha256']
assert hashlib.sha256((root/'results/tokenizer.json').read_bytes()).hexdigest()==expected, 'Tokenizer changed: obtain original revision matching manifest hash'
