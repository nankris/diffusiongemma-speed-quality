from pathlib import Path
import subprocess
p=Path('/content/llama.cpp/examples/diffusion/diffusion-cli.cpp')
s=p.read_text();s='#include <fstream>\n'+s
s=s.replace('    llama_backend_init();','    params.enable_chat_template = false;\n    llama_backend_init();')
needle='    if (params.conversation_mode == COMMON_CONVERSATION_MODE_ENABLED) {'
assert s.count(needle)==1
insert=r'''
    if (const char * input_path = std::getenv("FAIR_INPUT")) {
        std::ifstream input(input_path);
        std::string prompt;
        int index = 0;
        const std::string dir = std::getenv("FAIR_DIR");
        while (std::getline(input, prompt, '\x1e')) {
            const auto response = run_turn_reply(prompt);
            const std::string stem = dir + "/dg_" + std::to_string(index++);
            { std::ofstream out(stem + ".out"); out << response; }
            { std::ofstream out(stem + ".done"); out << cb_data.steps_seen << " " << cb_data.blocks_seen; }
        }
    } else
'''
s=s.replace(needle,insert+needle)
# Retain exact engine-only turn time, independent of log flush overhead.
s=s.replace('        const int64_t turn_us = ggml_time_us() - t0;','''        const int64_t turn_us = ggml_time_us() - t0;
        if (const char * dir = std::getenv("FAIR_DIR")) {
            static int fair_index = 0;
            std::ofstream out(std::string(dir) + "/dg_" + std::to_string(fair_index++) + ".ms");
            out << turn_us / 1000.0;
        }''')
needle_cap='        return common_detokenize(vocab, response, false);'
assert s.count(needle_cap)==1
s=s.replace(needle_cap,'        if (params.n_predict > 0 && response.size() > (size_t) params.n_predict) response.resize(params.n_predict);\n'+needle_cap)
p.write_text(s)
Path('/content/current/source.patch').write_text(subprocess.check_output(['git','-C','/content/llama.cpp','diff'],text=True))
