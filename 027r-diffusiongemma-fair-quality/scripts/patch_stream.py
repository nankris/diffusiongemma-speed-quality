import pathlib,subprocess,time
p=pathlib.Path('/content/r027r/raw_prompt.patch')
while not p.exists():time.sleep(3)
f=pathlib.Path('/content/llama.cpp/examples/diffusion/diffusion-cli.cpp');s=f.read_text()
needle='        run_turn_reply(formatted);'
assert s.count(needle)==1
s=s.replace(needle,'''        if (!formatted.empty()) {
            run_turn_reply(formatted);
        }
        LOG("\\n> ");
        common_log_flush(common_log_main());
        while (std::getline(std::cin, formatted, '\\x1e')) {
            run_turn_reply(formatted);
            LOG("\\n> ");
            common_log_flush(common_log_main());
        }''')
f.write_text(s)
subprocess.run(['cmake','--build','/content/llama.cpp/build','-j2','--target','llama-diffusion-cli','llama-server'],check=True)
(P:=pathlib.Path('/content/r027r/stream_prompt.patch')).write_text(subprocess.check_output(['git','-C','/content/llama.cpp','diff'],text=True))
print('Stream build done',flush=True)
