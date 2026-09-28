# OpenCode vLLM Push-T setup v3

This worktree uses the v2 vLLM provider configuration: the API-compatible base URL comes from `API_URL`, the key comes from `API_KEY`, and reasoning effort remains low. No endpoint or key is stored in the repository.

## Start OpenCode

Use the v3 worktree root and expected branch:

```bash
cd ../ENPIRE_opencode_test_v3
git rev-parse --show-toplevel
git branch --show-current
git submodule update --init --recursive
export API_URL="http://<your-vllm-host>:8000/v1"
read -r -s -p 'API key: ' API_KEY
export API_KEY
printf '\n'
opencode
```

Enter the API base URL ending in `/v1`, not a `/v1/models` listing URL. Do not echo the key or save either credential in repository files, prompts, logs, or experiment folders. Paste `OPENCODE_PUSHT_AUTORESEARCH_PROMPT_V3.md` into OpenCode from the worktree root.

## V3 run rules

The prompt and `autoresearch_runs/pusht/EXPERIMENT_PROTOCOL.md` define one baseline plus at most ten complete candidate episodes, with no scratch simulations. Every run's hypothesis, policy snapshot, diff, decision, wrapper log, result, events, final frame, and GIF belong in that run's own ignored directory under `outputs/autoresearch/pusht/experiments/`.

The timing wrapper and aggregate CSV remain under `autoresearch_runs/pusht/`. Generated `outputs/`, logs, and CSV are ignored by Git so the reusable setup branch can be shared without publishing experiment artifacts. Do not commit or push from the OpenCode session.

## Reuse from another folder

Clone the reusable branch into a separate folder:

```bash
git clone --branch opencode-vllm-test-v3 --single-branch <repository-url> ENPIRE_opencode_test_v3
cd ENPIRE_opencode_test_v3
```

Alternatively, create another linked worktree from the branch:

```bash
git fetch origin
git worktree add -b <new-run-branch> ../<new-folder> origin/opencode-vllm-test-v3
```

For a different branch name, change the expected branch in the v3 kickoff prompt before using it.
