#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Use any Python environment containing requirements.txt; PYTHON may select it.
PYTHON="${PYTHON:-python}"
test -f results/FINISHED
"$PYTHON" scripts/get_tokenizer.py
"$PYTHON" scripts/validate.py > results/validation.json
"$PYTHON" scripts/analyze.py
"$PYTHON" scripts/report.py
