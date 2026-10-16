from pathlib import Path
p=Path('/content/llama.cpp/examples/diffusion/diffusion-cli.cpp')
s=p.read_text()
s='#include <fstream>\n#include "json.hpp"\n'+s
s=s.replace('inputs.add_generation_prompt = true;', 'inputs.add_generation_prompt = true;\n        inputs.enable_thinking = false;')
needle='    if (params.conversation_mode == COMMON_CONVERSATION_MODE_ENABLED) {'
insert=r'''
    if (const char * batch_path = std::getenv("FAIR_PROMPTS")) {
        std::ifstream in(batch_path);
        std::ofstream out(std::getenv("FAIR_OUTPUT"));
        std::string user;
        int index = 0;
        while (std::getline(in, user)) {
            std::vector<common_chat_msg> messages;
            messages.push_back(make_msg("user", user));
            const std::string formatted = apply_template(messages);
            if (index == 0) { LOG_INF("FAIR_FORMATTED_PROMPT: %s\n", formatted.c_str()); }
            const int64_t start = ggml_time_us();
            const std::string response = run_turn_reply(formatted);
            const double ms = (ggml_time_us() - start) / 1000.0;
            nlohmann::ordered_json row;
            row["index"] = index++;
            row["response"] = response;
            row["elapsed_ms"] = ms;
            row["tokens"] = common_tokenize(vocab, response, false, true).size();
            row["steps"] = cb_data.steps_seen;
            row["blocks"] = cb_data.blocks_seen;
            out << row.dump() << std::endl;
        }
    } else
'''
assert needle in s
s=s.replace(needle,insert+needle)
p.write_text(s)
print('patched batch input and enable_thinking=false')
