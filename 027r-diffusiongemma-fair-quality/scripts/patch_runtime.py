from pathlib import Path
import subprocess
root=Path('/content/llama.cpp')
p=root/'examples/diffusion/diffusion-cli.cpp'
s=p.read_text().replace('        inputs.enable_thinking = false;\n','')
s=s.replace('inputs.add_generation_prompt = true;', 'inputs.add_generation_prompt = true;\n        inputs.enable_thinking = false;')
s=s.replace('return common_chat_templates_apply(chat_templates.get(), inputs).prompt.str();','const auto fair_prompt = common_chat_templates_apply(chat_templates.get(), inputs).prompt.str();\n        LOG_INF("FAIR_TEMPLATE: %s\\n", fair_prompt.c_str());\n        return fair_prompt;')
p.write_text(s)
p=root/'tools/completion/completion.cpp';s=p.read_text()
s=s.replace('inputs.force_pure_content = params.force_pure_content_parser;', 'inputs.force_pure_content = params.force_pure_content_parser;\n                inputs.enable_thinking = false;')
s=s.replace('prompt = common_chat_templates_apply(chat_templates.get(), inputs).prompt.str();','prompt = common_chat_templates_apply(chat_templates.get(), inputs).prompt.str();\n                LOG_INF("FAIR_TEMPLATE: %s\\n", prompt.c_str());')
p.write_text(s)
patch=subprocess.getoutput('git -C /content/llama.cpp diff -- examples/diffusion/diffusion-cli.cpp tools/completion/completion.cpp')
(root.parent/'r027r/runtime.patch').write_text(patch)
print(patch)
