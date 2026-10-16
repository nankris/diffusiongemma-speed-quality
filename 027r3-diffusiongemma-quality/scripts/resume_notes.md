# Resume procedure

Do not regenerate completed answers. While runtime r3027 is live, stop only the failed runner process if needed, preserve /content/current/answers, upload scripts/remote_run.py, and launch it detached as in results/launch_run.py. It skips every existing per-arm JSON answer and starts a new persistent model only for missing answers. It pauses at WAITING until a local snapshot is downloaded and ACK_<label> is touched. scripts/controller.py is the complete original allocation controller; do not blindly restart it over a live scored run because it starts setup. Use its snapshot function/remote_status.py to recover local answers first.

If the runtime is lost, allocate a replacement only within remaining experiment CU and wall time. Rebuild the pinned source, restore results/raw/answers to /content/current/answers, restore the original prompts.json, set /content/current/deadline conservatively, launch remote_run.py. Do not restore .out/.done/.ms staging files: per-answer JSONs are canonical. Repeat snapshot/download/ACK at each batch. Account for every allocation and always stop only this experiment's own runtime. No automatic replacement allocation is hidden in these scripts.

Statistics are run once at the fixed completed n=300. Partial data are recoverable, but must not trigger an interim inferential decision.
