#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source /workspace/tools/setup.sh
if test -f results/FINISHED; then
 echo 'Finished: analyze saved files; do not allocate again.'
 exit 0
fi
# Only resume the owned existing r5g027 allocation within its saved deadline.
# If runtime is gone, preserve results and finish infrastructure report; no automatic fresh budget.
colab status -s r5g027
python scripts/controller.py
