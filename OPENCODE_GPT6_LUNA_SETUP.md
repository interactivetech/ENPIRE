# OpenCode GPT-6 Luna Push-T comparison setup

This worktree selects the exact model ID `gpt-6-luna` through the OpenAI-compatible CLIProxyAPI provider. The API base URL comes from `API_URL`, the key comes from `API_KEY_2`, and reasoning effort remains low to match the v3 GLM comparison setup. The key is not stored in the repository.

## Start OpenCode

Use the GPT-6 Luna worktree root and expected branch:

```bash
cd <path-to-ENPIRE_opencode_gpt6_luna>
git rev-parse --show-toplevel
git branch --show-current
git submodule update --init --recursive
export API_URL="http://127.0.0.1:8317/v1"
read -r -s -p 'CLIProxyAPI key: ' API_KEY_2
export API_KEY_2
printf '\n'
opencode
```

The URL must be the API base ending in `/v1`, not the `/v1/models` listing URL. If CLIProxyAPI is bound to a different host/port, set `API_URL` to that base instead. Do not echo the key or save either credential in repository files, prompts, logs, or experiment folders. Paste `OPENCODE_PUSHT_AUTORESEARCH_PROMPT_GPT6_LUNA.md` into OpenCode from the worktree root.

## V3 run rules

The prompt and `autoresearch_runs/pusht/EXPERIMENT_PROTOCOL.md` define one baseline plus at most ten complete candidate episodes, with no scratch simulations. Every run's hypothesis, policy snapshot, diff, decision, wrapper log, result, events, final frame, and GIF belong in that run's own ignored directory under `outputs/autoresearch/pusht/experiments/`.

The model route and API connection differ from the GLM v3 setup. Keep the task, baseline, ten-candidate cap, reasoning effort, seed, and step budget unchanged for comparison. The timing wrapper and aggregate CSV remain under `autoresearch_runs/pusht/`. Generated `outputs/`, logs, and CSV are ignored by Git so the reusable setup branch can be shared without publishing experiment artifacts. Do not commit or push from the OpenCode session.

## Reuse from another folder

Clone the reusable branch into a separate folder:

```bash
git clone --branch opencode-gpt6-luna-pusht --single-branch <repository-url> ENPIRE_opencode_gpt6_luna
cd ENPIRE_opencode_gpt6_luna
```

Alternatively, create another linked worktree from the branch:

```bash
git fetch origin
git worktree add -b <new-run-branch> ../<new-folder> origin/opencode-gpt6-luna-pusht
```

For a different branch name, change the expected branch in the GPT-6 Luna kickoff prompt before using it.
