# OpenCode vLLM Push-T setup

This checkout contains the simulated Push-T task, the v2 autoresearch prompt, and a timing wrapper. The OpenCode provider configuration reads both endpoint and key from the process environment; neither is stored in the repository.

## Configure and launch

Set `API_URL` to the OpenAI-compatible API base URL ending in `/v1` (use the API root, not a `/v1/models` listing URL). Supply the key without echoing it or saving it in shell history, then start OpenCode from the repository root:

```bash
export API_URL="http://<your-vllm-host>:8000/v1"
read -r -s -p 'API key: ' API_KEY
export API_KEY
printf '\n'
opencode
```

Paste the contents of `OPENCODE_PUSHT_AUTORESEARCH_PROMPT_V2.md`. It verifies the checkout root and branch before work begins. If you use a different branch name, update the expected branch in the prompt first.

## Reuse in another folder

For a separate clone, check out the pushed branch into a new folder:

```bash
git clone --branch opencode-vllm-test-v2 --single-branch <repository-url> <new-folder>
cd <new-folder>
```

For a second linked worktree in the same clone, use a new local branch based on the reusable branch because Git cannot check out one local branch in two linked worktrees at once:

```bash
git fetch origin
git worktree add -b <new-run-branch> ../<new-folder> origin/opencode-vllm-test-v2
```

Change the prompt's expected branch name to `<new-run-branch>` before launching. Set `API_URL` and `API_KEY` in that shell as above.

## Baseline and timing

Run artifacts under `outputs/` are local and ignored by Git. If the checkout does not contain `outputs/autoresearch/pusht/baseline/result.json`, the prompt directs OpenCode to create the seed-0, 300-step baseline once through the timing wrapper. It will not overwrite an existing baseline.

Every scratch and official evaluation must use `autoresearch_runs/pusht/time_experiment.py`. It appends UTC timestamps, monotonic wall-clock seconds, experiment kind, hypothesis, result metrics, and artifact/log paths to `autoresearch_runs/pusht/experiment_timing.csv`; captured output goes under `autoresearch_runs/pusht/experiment_logs/`. Keep all experiment code, scratch runs, snapshots, logs, and episode outputs in the selected checkout.
