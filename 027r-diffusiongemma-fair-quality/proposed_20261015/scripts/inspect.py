import subprocess
from pathlib import Path
print(subprocess.getoutput('cat /content/r027/status; tail -4 /content/r027/build.log'))
for p in Path('/content/llama.cpp/examples').rglob('*diffusion*'):
 print(p)
 if p.is_file() and p.suffix=='.cpp':
  text=p.read_text()
  Path('/content/diffusion-source.txt').write_text(text)
  for i,line in enumerate(text.splitlines()):
   if any(x in line for x in ['thinking','chat_template','while (','getline','interactive','prompt_file','main(']):print(i,line)
