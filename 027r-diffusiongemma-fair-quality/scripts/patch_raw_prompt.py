import pathlib,subprocess,time
p=pathlib.Path('/content/r027r/status')
while not(p.exists() and 'ALL_SETUP_DONE' in p.read_text()):time.sleep(5)
f=pathlib.Path('/content/llama.cpp/examples/diffusion/diffusion-cli.cpp')
s=f.read_text();needle='    llama_backend_init();';assert s.count(needle)==1
s=s.replace(needle,'    params.enable_chat_template = false;\n\n'+needle);f.write_text(s)
subprocess.run(['cmake','--build','/content/llama.cpp/build','-j2','--target','llama-diffusion-cli'],check=True)
patch=subprocess.check_output(['git','-C','/content/llama.cpp','diff'],text=True);pathlib.Path('/content/r027r/raw_prompt.patch').write_text(patch)
subprocess.run(['python3','/content/probe.py'],check=True)
