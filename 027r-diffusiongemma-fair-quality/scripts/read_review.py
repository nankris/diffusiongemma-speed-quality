from pathlib import Path
p=Path('/content/llama.cpp/skills/code-review/SKILL.md');print(p.read_text() if p.exists() else 'Not present')
