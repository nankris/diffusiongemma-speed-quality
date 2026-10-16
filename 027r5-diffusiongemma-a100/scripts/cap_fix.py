from pathlib import Path
import subprocess
p=Path('/content/llama.cpp/examples/diffusion/diffusion-cli.cpp')
s=p.read_text();needle='        return common_detokenize(vocab, response, false);'
insert='        if (params.n_predict > 0 && response.size() > (size_t) params.n_predict) response.resize(params.n_predict);'
if insert not in s:
 assert s.count(needle)==1
 p.write_text(s.replace(needle,insert+'\n'+needle))
Path('/content/current/source.patch').write_text(subprocess.check_output(['git','-C','/content/llama.cpp','diff'],text=True))
print('DG strict returned-token cap applied before build of diffusion-cli')
