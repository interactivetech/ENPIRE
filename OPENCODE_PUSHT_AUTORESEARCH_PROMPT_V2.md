# OpenCode prompt: Push-T autoresearch v2

Launch OpenCode from the root of the `opencode-vllm-test-v2` worktree, then paste this prompt:

```text
Read AGENTS.md, enpire/policy/autoresearch_instruction.md, enpire/env/examples/20_simulated_pusht/README.md, and autoresearch_runs/pusht/TIMING_LOGGING.md.

First run `pwd`, `git rev-parse --show-toplevel`, and `git branch --show-current`. Confirm that the current working directory is the Git root and that the branch is `opencode-vllm-test-v2`. If either check fails, stop and report the paths. Do not switch to another checkout.

Keep all experiment code, scratch files, logs, snapshots, and outputs beneath this repository root. Do not use `/tmp`, system temp directories, `$HOME`, or another checkout for experiment work. Store scratch scripts and data under `autoresearch_runs/pusht/scratch/`; store each scratch run in a unique `autoresearch_runs/pusht/scratch_runs/<experiment-id>/`; store official episode artifacts in fresh `outputs/autoresearch/pusht/iteration-N/` directories. Use only repository-relative paths and check `git status --short` after each experiment.

Use `python autoresearch_runs/pusht/time_experiment.py` for EVERY experiment run: every scratch prototype, parameter sweep point, failed or invalid run, and official ENPIRE evaluation. One wrapper invocation must represent one configuration/run; do not batch several configurations inside one timed invocation. Give every run a unique ID. The wrapper records UTC start/end timestamps, monotonic wall-clock seconds, run kind, hypothesis, exit code, artifact path, log path, and metrics from result.json when present in `autoresearch_runs/pusht/experiment_timing.csv`. It keeps stdout/stderr under `autoresearch_runs/pusht/experiment_logs/`. Do not write credentials or secret values to commands, hypotheses, logs, or artifacts.

For a scratch experiment, save its script below `autoresearch_runs/pusht/scratch/`, make it write a result.json with coverage, success, and elapsed_s under its unique scratch run directory, and invoke it like this (replace the ID and text each time):

`python autoresearch_runs/pusht/time_experiment.py --experiment-id scratch-001 --kind scratch --label "short description" --hypothesis "falsifiable statement" --artifact-dir autoresearch_runs/pusht/scratch_runs/scratch-001 -- uv run python autoresearch_runs/pusht/scratch/prototype_001.py --output-dir autoresearch_runs/pusht/scratch_runs/scratch-001`

For each official candidate, use the same timing wrapper, but set `--kind official`, use `--artifact-dir outputs/autoresearch/pusht/iteration-N`, and run `uv run enpire examples run 20_simulated_pusht --output outputs/autoresearch/pusht/iteration-N` after `--`. Do not overwrite the baseline or any prior run.

Focus exclusively on simulated Push-T policy performance. Use final T-block coverage as the score (higher is better); success requires at least 0.95. Keep seed 0 and the 300-step budget fixed for official evaluations. Only edit policy/action-selection code in `enpire/env/examples/20_simulated_pusht/example.py`. Do not change simulator dynamics, reset behavior, observations, reward, verification, success threshold, safety behavior, or artifact format. Do not use real hardware, commit, or push.

Record one falsifiable hypothesis before every experiment, including scratch runs. Record its experiment ID, hypothesis, source diff/snapshot, coverage, success, and keep/revert decision in `autoresearch_runs/pusht/iterations.md`. Preserve failed runs and their timing rows. Keep a candidate only if official final coverage strictly improves on the best official result; restore the best policy after any worse or tied candidate.

At completion, verify that every experiment in the journal has exactly one corresponding row in `autoresearch_runs/pusht/experiment_timing.csv`. Report scratch and official run counts, each run's wall-clock seconds, cumulative elapsed wall time from first timed run to last timed run, official best coverage/success, and the current diff. Do not call the sum of simulator elapsed_s values the research wall-clock duration.
```
